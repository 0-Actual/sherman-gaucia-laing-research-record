# GAUCIA — retained application source and repair history

GAUCIA is the project's local conversation application. The supplied source implements local records, retrieval, a model-backend wrapper, a Windows interface, a local communication panel and bounded numerical functions. Owner/project: Sherman Gaucia Laing / Quantum.Earth.Laing. Preserve the authorship and AI-assistance notices in the source.

Read the [October 18 availability correction](PUBLICATION_CORRECTION_20261018.md) and the dated [revision 2 review](PUBLICATION_REVIEW_R2.md) first.

## Which version is which

- **GAUCIA-historical** contains the retained application source and selected documentary evidence. Its original status records are dated snapshots.
- **GAUCIA-repair-r3** contains the later repair sources, regression tests, native-interface source, baseline versions and installation tooling. The source bundle's original “not deployed” label predates the later installation receipt; it must not be used as a current statement about the owner's installed application.
- **GAUCIA-service-corrections-r4** adds the reviewed backend exit-confirmation repair, both awaiting service callers and 55 passing isolated regression tests. Apply the replacement pair only after reviewing the integration instructions; no installed copy was changed.

Original private copies remain preserved. Public copies remove private conversation state and use an empty research-corpus configuration. Readers must supply their own permitted research inputs. The application source does not distribute the owner's live conversation history, model weights or private authentication material.

## Reproduction and dependencies

The historical application source and repair package are separate snapshots. To study the corrected implementation, compare the repair's `service/` files against the historical application's corresponding files and the retained `baseline/` versions. Keep that comparison distinct from installing or running the application.

The application expects Node.js, a compatible local llama-server runtime and a model supplied under its own terms. This edition's configuration uses reader-supplied paths under `runtime/` and `models/`, with an empty `corpus` list. It is not an installer or a claim that a language model was trained from scratch.

The communication-panel source references `turn-audit.mjs` and `watchdog.mjs`. At the October 17 preparation, these files were absent from the selected laptop copy and the required USB reads were denied. On October 18, both actual source files were recovered internally and their recorded identities matched. The earlier limitation described the publication selection and access at that time, not loss of the research. The recovered sources are not newly distributed here, and a complete fresh installation of the public panel remains unverified. See the [dated availability correction](PUBLICATION_CORRECTION_20261018.md) for scope and isolated test evidence.

The repair package retains tests for record recovery, library behavior, startup, shutdown and native lifecycle boundaries. Existing results are historical execution evidence. The release's packaging checks are not a rerun of those suites or a new live USB/application test. Device-path sanitization can require adaptation of historical launch or installation scripts; such changes are identified as derivatives in the collection manifest.

## Known limitations

The backend shutdown-completion defect is now reproduced and corrected in r4. Acknowledgement identity binding remains a historical review candidate outside this correction; no exploitation or data-loss event is established. Do not interpret this bounded repair as an all-issues-fixed claim.

The numerical engine implements selected classical simulations. Four-row training examples and saved classifier outcomes do not establish held-out performance or generalization. Local retrieval, simulation, language-model inference, model-weight training and physical quantum computation are different operations.

Fingerprints recorded by application code are not automatically cryptographic signatures. The publication commit's verification status must be checked separately; it does not retroactively sign old application records or certify their conclusions.

## Governance

The Bible build and governance documents express the project's stated values and evidence discipline. They do not create operating-system access, independent certification or a guarantee of safe use. Existing stop/hold checks are preserved in historical code; this publication does not activate, remove or override a hold in the owner's installed environment.
