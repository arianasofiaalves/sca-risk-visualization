# SCA Risk Visualization

This project implements a prototype for visual risk prioritization of Software Composition Analysis (SCA) results using SBOM-based dependency graphs in Python open-source projects.

## Project Pipeline

1. Extract dependencies from Python projects
2. Normalize dependency data
3. Enrich dependencies with vulnerability and license information
4. Build dependency graphs
5. Apply a lightweight risk scoring model
6. Generate visual outputs for prioritization