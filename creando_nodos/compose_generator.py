#!/usr/bin/env python3
import sys, os, glob, json, yaml, copy

CLASSES       = ['XCBR', 'MMXU']
SERVICE_MAP   = {'XCBR': 'virtual-circuit-breaker', 'MMXU': 'virtual-104-gtw'}
PREFIX_MAP    = {'XCBR': 'XBCR',            'MMXU': 'reader'}
CLASS_DEPENDS = {'XCBR': [],                 'MMXU': ['XCBR']}

if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
    json_file = sys.argv[1]
else:
    matches = glob.glob(os.path.join('creando_nodos','archivos_xml','*.json'))
    if not matches:
        print("Error: no se encontró JSON en creando_nodos/archivos_xml/*.json")
        sys.exit(1)
    json_file = matches[0]

print("➜ JSON de nodos:", json_file)

base_compose = os.path.join(os.getcwd(), 'docker-compose-base.yml')
if not os.path.isfile(base_compose):
    print(f"Error: no existe {base_compose}")
    sys.exit(1)
print("➜ Compose base:", base_compose)

with open(base_compose, 'r', encoding='utf-8') as f:
    base = yaml.safe_load(f)

base_services = base.get('services', {})
base_networks = base.get('networks', {})

templates = {}
for cls, svc in SERVICE_MAP.items():
    if svc not in base_services:
        print(f"Error: servicio base '{svc}' no está en docker-compose.yml")
        sys.exit(1)
    templates[cls] = base_services.pop(svc)

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

elements = []
for ied in data:
    for ap in ied.get('AccessPoints', []):
        for ld in ap.get('LogicalDevices', []):
            ln0 = ld.get('LN0')
            if isinstance(ln0, dict) and ln0.get('lnClass') in CLASSES:
                elements.append(ln0)
            for ln in ld.get('LogicalNodes', []):
                if ln.get('lnClass') in CLASSES:
                    elements.append(ln)

counts = {cls: 0 for cls in CLASSES}
for e in elements:
    cls = e.get('lnClass')
    if cls in counts:
        counts[cls] += 1

print("➜ Instancias detectadas:")
for cls, n in counts.items():
    print(f"   • {cls}: {n}")

dynamic_services = {}
for cls, num in counts.items():
    if num < 1: 
        continue
    template = templates[cls]
    for i in range(1, num+1):
        base_name = SERVICE_MAP[cls]
        svc_key   = base_name if num == 1 else f"{base_name}-{i}"
        
        cfg = copy.deepcopy(template)
        cfg['container_name'] = f"{PREFIX_MAP[cls]}-{i}"
        
        deps = []
        for dep in CLASS_DEPENDS.get(cls, []):
            for j in range(1, counts[dep] + 1):
                dep_name = SERVICE_MAP[dep] if counts[dep] == 1 else f"{SERVICE_MAP[dep]}-{j}"
                deps.append(dep_name)
        if deps:
            cfg['depends_on'] = deps

        dynamic_services[svc_key] = cfg

output_file = os.path.join(os.getcwd(), 'docker-compose.yml')
def remove_if_exists(path):
    try:
        os.remove(path)
        print(f"* Eliminado existente: {path}")
    except FileNotFoundError:
        pass

remove_if_exists(output_file)

new_compose = {
    'version': base.get('version', '3.8'),
    'services': {**base_services, **dynamic_services},
    'networks': base_networks
}

with open(output_file, 'w', encoding='utf-8') as f:
    yaml.dump(new_compose, f, sort_keys=False, default_flow_style=False)
print(f"✅ {output_file} creado con {len(new_compose['services'])} servicios.")
