import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("backend")

class RequestloggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        start_time = time.time()

        # Leer cuerpo de la request (Streamlit -> FastAPI)
        try:
            body = await request.body()
        except:
            body = b""
        
        logger.info(f"REQUEST: {request.method} {request.url.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        #logger.info(f'Body: {body.decode("utf-8", errors= "ignore")}')
        #logger.info(f"JSON: {request.json()}")
        
        content_type = request.headers.get("content-type", "")

        if "multipart/form-data" in content_type or "application/pdf" in content_type:
            logger.info("Body: [BINARY DATA OMITTED]")
        else:
            logger.info(f"Body: {body.decode('utf-8', errors= "replace")}")

        # Ejecutar la request
        try:
            response = await call_next(request)

        except Exception as e:
            logger.error(f"ERROR durante la ejecución del endopoint: {e}")
            raise e

        max_logs = 2000

        # Solo loguear JSON

        # Log seguro para binarios (como pdf)
        if response.media_type == "application/json":
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            decoded_resp = response_body.decode('utf-8', errors= "replace")
            logger.info(f"RESPONSE BODY DETAILS: {decoded_resp[:1500]} ... [TRUNCATED]")
            duration = (time.time() - start_time) * 1000
            logger.info(f"RESPONSE: {response.status_code} en {duration:.2f}ms")

            # Devolver el response original
            return Response(
                content= response_body,
                status_code= response.status_code,
                headers= dict(response.headers),
                media_type= "application/json"
            )
        else:
            
            logger.info("RESPONSE BODY DETAILS: [BINARY DATA OMITTED]")
            return response













