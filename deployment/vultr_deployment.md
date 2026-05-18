# Vultr Deployment Guide

## Option A: Docker on a Vultr VM

1. Create a Vultr Ubuntu VM.
2. SSH into the VM.
3. Install Docker.
4. Clone the GitHub repository.
5. Create `.env` from `.env.example`.
6. Add your Featherless API key.
7. Build and run the container.

```bash
git clone YOUR_REPO_URL
cd menutaste-featherless-starter
cp .env.example .env
nano .env

docker build -t menutaste-featherless .
docker run -d --name menutaste -p 80:8501 --env-file .env menutaste-featherless
```

Then open:

```text
http://YOUR_VULTR_SERVER_IP
```

## Production Notes

- Use a domain name for the final demo URL.
- Use HTTPS if time allows.
- Do not commit `.env`.
- Keep the Featherless API key private.
