import { Dwg_File_Type, LibreDwg } from '@mlightcad/libredwg-web';
import fs from 'fs';
const lib = await LibreDwg.create('./node_modules/@mlightcad/libredwg-web/wasm/');
const buf = fs.readFileSync(process.argv[2]);
const dwg = lib.dwg_read_data(buf, Dwg_File_Type.DWG);
const db = lib.convert(dwg);
const out = { layers: db.tables?.LAYER?.entries?.map(l => l.name), entities: [] };
const types = {};
for (const e of db.entities) {
  types[e.type] = (types[e.type] || 0) + 1;
  if (e.type === 'LWPOLYLINE' || e.type === 'POLYLINE2D' || e.type === 'LINE' || e.type === 'ARC' || e.type === 'CIRCLE' || e.type === 'SPLINE' || e.type === 'TEXT' || e.type === 'HATCH' || e.type==='POLYLINE')
    out.entities.push(e);
}
out.types = types;
fs.writeFileSync(process.argv[3], JSON.stringify(out, (k, v) => typeof v === "bigint" ? Number(v) : v));
console.log(JSON.stringify(types), 'layers', out.layers?.length);
