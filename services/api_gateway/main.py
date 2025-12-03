from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional

app = FastAPI(
    title="API Gateway - Sistema de Gestión TI",
    description="Punto de entrada único para todos los microservicios",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de los microservicios
EQUIPOS_SERVICE_URL = os.getenv("EQUIPOS_SERVICE_URL", "http://equipos-service:8001")
PROVEEDORES_SERVICE_URL = os.getenv("PROVEEDORES_SERVICE_URL", "http://proveedores-service:8002")
MANTENIMIENTO_SERVICE_URL = os.getenv("MANTENIMIENTO_SERVICE_URL", "http://mantenimiento-service:8003")
REPORTES_SERVICE_URL = os.getenv("REPORTES_SERVICE_URL", "http://reportes-service:8004")
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8005")

# Cliente HTTP asíncrono
client = httpx.AsyncClient(timeout=30.0)

@app.get("/health")
async def health_check():
    """Health check del API Gateway"""
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/")
async def root():
    """Endpoint raíz con información del API Gateway"""
    return {
        "message": "API Gateway - Sistema de Gestión de Equipos de TI",
        "version": "1.0.0",
        "endpoints": {
            "equipos": "/api/equipos",
            "proveedores": "/api/proveedores",
            "mantenimientos": "/api/mantenimientos",
            "reportes": "/api/reportes",
            "agents": "/api/agents",
            "docs": "/docs"
        }
    }

# ==================== RUTAS DE EQUIPOS ====================

@app.api_route("/api/equipos/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/equipos", methods=["GET", "POST"])
async def proxy_equipos(request: Request, path: Optional[str] = None):
    """Proxy para el servicio de equipos"""
    url = f"{EQUIPOS_SERVICE_URL}/equipos"
    if path:
        url = f"{EQUIPOS_SERVICE_URL}/equipos/{path}"
    
    try:
        params = dict(request.query_params)
        
        # Obtener JSON body si existe
        json_body = None
        body_content = None
        content_type = request.headers.get("content-type", "")
        
        if request.method in ["POST", "PUT", "PATCH"]:
            if content_type.startswith("application/json"):
                try:
                    json_body = await request.json()
                except:
                    body_content = await request.body()
            else:
                body_content = await request.body()
        
        response = await client.request(
            method=request.method,
            url=url,
            params=params,
            json=json_body if json_body else None,
            content=body_content if body_content else None,
            headers={k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
        )
        
        # Manejar errores HTTP
        if response.status_code >= 400:
            try:
                error_data = response.json()
                return JSONResponse(content=error_data, status_code=response.status_code)
            except:
                return JSONResponse(
                    content={"detail": response.text or "Error del servidor"},
                    status_code=response.status_code
                )
        
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de equipos: {str(e)}")
    except Exception as e:
        import traceback
        print(f"Error en proxy_equipos: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.api_route("/api/categorias", methods=["GET"])
async def proxy_categorias(request: Request):
    """Proxy para categorías de equipos"""
    try:
        response = await client.get(f"{EQUIPOS_SERVICE_URL}/categorias")
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de equipos: {str(e)}")

@app.api_route("/api/ubicaciones", methods=["GET"])
async def proxy_ubicaciones(request: Request):
    """Proxy para ubicaciones"""
    try:
        response = await client.get(f"{EQUIPOS_SERVICE_URL}/ubicaciones")
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de equipos: {str(e)}")

@app.api_route("/api/movimientos", methods=["POST"])
async def proxy_movimientos(request: Request):
    """Proxy para movimientos de equipos"""
    try:
        body = await request.json()
        response = await client.post(f"{EQUIPOS_SERVICE_URL}/movimientos", json=body)
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de equipos: {str(e)}")

# ==================== RUTAS DE PROVEEDORES ====================

@app.api_route("/api/proveedores/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/proveedores", methods=["GET", "POST"])
async def proxy_proveedores(request: Request, path: Optional[str] = None):
    """Proxy para el servicio de proveedores"""
    url = f"{PROVEEDORES_SERVICE_URL}/proveedores"
    if path:
        url = f"{PROVEEDORES_SERVICE_URL}/proveedores/{path}"
    
    try:
        params = dict(request.query_params)
        
        # Obtener JSON body si existe
        json_body = None
        body_content = None
        content_type = request.headers.get("content-type", "")
        
        if request.method in ["POST", "PUT", "PATCH"]:
            if content_type.startswith("application/json"):
                try:
                    json_body = await request.json()
                except:
                    body_content = await request.body()
            else:
                body_content = await request.body()
        
        response = await client.request(
            method=request.method,
            url=url,
            params=params,
            json=json_body if json_body else None,
            content=body_content if body_content else None,
            headers={k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
        )
        
        # Manejar errores HTTP
        if response.status_code >= 400:
            try:
                error_data = response.json()
                return JSONResponse(content=error_data, status_code=response.status_code)
            except:
                return JSONResponse(
                    content={"detail": response.text or "Error del servidor"},
                    status_code=response.status_code
                )
        
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de proveedores: {str(e)}")
    except Exception as e:
        import traceback
        print(f"Error en proxy_proveedores: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.api_route("/api/contratos", methods=["GET", "POST"])
async def proxy_contratos(request: Request):
    """Proxy para contratos"""
    try:
        if request.method == "GET":
            params = dict(request.query_params)
            response = await client.get(f"{PROVEEDORES_SERVICE_URL}/contratos", params=params)
        else:
            body = await request.json()
            response = await client.post(f"{PROVEEDORES_SERVICE_URL}/contratos", json=body)
        
        # Manejar errores HTTP
        if response.status_code >= 400:
            try:
                error_data = response.json()
                return JSONResponse(content=error_data, status_code=response.status_code)
            except:
                return JSONResponse(
                    content={"detail": response.text or "Error del servidor"},
                    status_code=response.status_code
                )
        
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de proveedores: {str(e)}")
    except Exception as e:
        import traceback
        print(f"Error en proxy_contratos: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==================== RUTAS DE MANTENIMIENTOS ====================

@app.api_route("/api/mantenimientos/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/mantenimientos", methods=["GET", "POST"])
async def proxy_mantenimientos(request: Request, path: Optional[str] = None):
    """Proxy para el servicio de mantenimientos"""
    url = f"{MANTENIMIENTO_SERVICE_URL}/mantenimientos"
    if path:
        url = f"{MANTENIMIENTO_SERVICE_URL}/mantenimientos/{path}"
    
    try:
        body = await request.body()
        params = dict(request.query_params)
        
        response = await client.request(
            method=request.method,
            url=url,
            params=params,
            content=body if body else None,
            headers=dict(request.headers)
        )
        
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de mantenimientos: {str(e)}")

# ==================== RUTAS DE REPORTES ====================

@app.api_route("/api/reportes/{path:path}", methods=["GET", "POST"])
@app.api_route("/api/reportes", methods=["GET"])
async def proxy_reportes(request: Request, path: Optional[str] = None):
    """Proxy para el servicio de reportes"""
    from fastapi.responses import StreamingResponse
    
    url = f"{REPORTES_SERVICE_URL}"
    if path:
        url = f"{REPORTES_SERVICE_URL}/{path}"
    
    try:
        params = dict(request.query_params)
        
        if request.method == "POST":
            body = await request.json()
            response = await client.post(url, params=params, json=body)
        else:
            response = await client.get(url, params=params)
        
        # Si es un archivo binario (PDF o Excel), devolver como StreamingResponse
        content_type = response.headers.get("content-type", "")
        if "application/pdf" in content_type or "application/vnd.openxmlformats-officedocument" in content_type or "application/vnd.ms-excel" in content_type:
            headers = {}
            if "content-disposition" in response.headers:
                headers["Content-Disposition"] = response.headers["content-disposition"]
            
            return StreamingResponse(
                iter([response.content]),
                media_type=content_type,
                headers=headers
            )
        
        # Para respuestas JSON normales
        return JSONResponse(
            content=response.json() if content_type.startswith("application/json") else {"data": response.text},
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de reportes: {str(e)}")

# ==================== RUTAS DE AGENTES ====================

@app.api_route("/api/agents/{path:path}", methods=["GET", "POST", "PUT"])
@app.api_route("/api/agents", methods=["GET", "POST"])
async def proxy_agents(request: Request, path: Optional[str] = None):
    """Proxy para el servicio de agentes"""
    url = f"{AGENT_SERVICE_URL}"
    if path:
        url = f"{AGENT_SERVICE_URL}/{path}"
    
    try:
        params = dict(request.query_params)
        
        if request.method == "POST":
            response = await client.post(url, params=params)
        elif request.method == "PUT":
            response = await client.put(url, params=params)
        else:
            response = await client.get(url, params=params)
        
        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
            status_code=response.status_code
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error conectando con servicio de agentes: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    """Cerrar cliente HTTP al apagar"""
    await client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

