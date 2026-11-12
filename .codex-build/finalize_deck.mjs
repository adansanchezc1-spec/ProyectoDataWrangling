import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = path.resolve(".");
const skillDir = "C:/Users/ADAN/.codex/plugins/cache/openai-primary-runtime/presentations/26.929.10730/skills/presentations";
const runtimePython = "C:/Users/ADAN/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
const sourcePath = "C:/Users/ADAN/Downloads/carpeta slides/InmoInsight_Fase2_IHC_Diapositivas.pptx";
const finalPath = path.join(workspaceDir, "docs/ihc/fase2/entregables/InmoInsight_Fase2_IHC_Presentacion_Final.pptx");
const stagingDir = path.join(workspaceDir, ".codex-finalizer");
const candidatePath = path.join(stagingDir, "InmoInsight_Fase2_IHC_Presentacion_Final.candidate.pptx");

const { finalizePresentation } = await import(
  pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href,
);

await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
if (presentation.slides.items.length !== 13) {
  throw new Error(`Expected 13 slides, found ${presentation.slides.items.length}`);
}

await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const sourceHash = await (await import("node:crypto")).webcrypto.subtle.digest(
  "SHA-256",
  await fs.readFile(sourcePath),
);
const sourceSha256 = Buffer.from(sourceHash).toString("hex");

const result = await finalizePresentation({
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  explicitTotalSlideCount: 13,
  materializeLiteralChartWorkbooks: true,
  fontPolicy: {
    basis: "reference",
    families: ["Arial", "Cambria", "Calibri", "Courier New"],
    referencePath: sourcePath,
    referenceSha256: sourceSha256,
  },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "InmoInsight_Fase2_IHC_Presentacion_Final.validation.json"),
});

console.log(JSON.stringify({ finalPath, result }, null, 2));
