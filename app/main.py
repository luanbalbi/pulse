import os

from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/healthz", status_code=200)
async def healthz() -> dict[str, str]:
	"""Check that the process is running, without testing any dependencies."""
	return {"status": "ok"}


@app.get("/readyz", status_code=200)
async def readyz() -> dict[str, str]:
	"""Check that the app is ready to receive requests."""
	if os.getenv("FORCE_UNREADY") == "true":
		raise HTTPException(status_code=503, detail="Service unavailable")

	try:
		# TODO: Check the PostgreSQL connection.
		return {"status": "ready"}
	except Exception as exc:
		raise HTTPException(
			status_code=503,
			detail="Service unavailable",
		) from exc