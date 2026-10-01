import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const sourcePath = "C:/Users/ADAN/Downloads/carpeta slides/InmoInsight_Fase2_IHC_Diapositivas.pptx";
const outputDir = path.resolve(".codex-build/reference-inspection");
await fs.mkdir(outputDir, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
const snapshot = await presentation.inspect({
  kind: "deck,slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 60000,
});
await fs.writeFile(path.join(outputDir, "inspection.ndjson"), snapshot.ndjson);

const montage = await presentation.export({ format: "png", montage: true, scale: 1 });
await fs.writeFile(path.join(outputDir, "montage.png"), new Uint8Array(await montage.arrayBuffer()));

for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const preview = await presentation.slides.getItem(index).export({ format: "png", scale: 1 });
  await fs.writeFile(
    path.join(outputDir, `slide-${String(index + 1).padStart(2, "0")}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}
console.log(JSON.stringify({
  slides: presentation.slides.items.length,
  slideSize: presentation.slideSize,
  outputDir,
}));
