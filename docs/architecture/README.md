# Architecture

ReadRight is organized as a clean monorepo with a strict boundary between product UI, scientific reasoning, versioned content, and operational infrastructure.

Core data flow:

`Task -> Evidence -> Quality Gate -> Learner State -> Hypothesis -> Next Task / Action -> Verification -> Updated State`

The assessment engine should be independently testable from the web application.
