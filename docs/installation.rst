Installation
============

This section describes how to get DRMAAtic up and running on your system.

**Prerequisites:**  
- A Linux environment (for running the DRMAAtic server and cluster scheduler).  
- (For manual install) An HPC scheduler like **SLURM** with DRMAA libraries installed, or use the provided Docker setup.  
- Python 3.8+ and Django (if installing from source) or Docker Engine (if using containers).

### Using Docker (Recommended)

The easiest way to deploy DRMAAtic is via Docker containers&#8203;:contentReference[oaicite:8]{index=8}. The project provides Docker Compose configurations for a full test cluster and a standalone deployment:

1. **Clone the repository** and navigate to the `docker/` directory:
   ```bash
   git clone https://github.com/BioComputingUP/DRMAAtic.git
   cd DRMAAtic/docker
