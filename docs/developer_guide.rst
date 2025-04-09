Developer Guide
===============

Architecture
------------
- Django project under `server/`
- Main app: `drmaatic/` with `task/` and `job/` modules
- Uses Django REST Framework and drmaa-python

Development Setup
-----------------
1. Fork and clone repo
2. Create a virtualenv and install:
   pip install -r requirements.txt -r dev-requirements.txt
3. Use docker/testing for SLURM
4. Run migrations and createsuperuser
5. Start development server

Running Tests
-------------
Run with:
   python manage.py test

Contributing
------------
- Follow PEP8
- Use Django/DRF best practices
- Document new features
- Submit PRs to `dev` branch

Advanced Configuration
----------------------
- Settings via `.env`
- Customize auth providers (e.g., ORCID)
- Job execution uses DRMAA (or shell scripts)
