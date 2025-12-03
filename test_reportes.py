#!/usr/bin/env python3
"""
Script de prueba para verificar la generación de reportes PDF y Excel
"""

import requests
import os
from datetime import datetime

API_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

def test_pdf_export(report_type="equipos"):
    """Prueba la exportación de PDF"""
    print(f"\n🔍 Probando exportación PDF para: {report_type}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/reportes/export/pdf",
            json={"type": report_type},
            timeout=30
        )
        
        if response.status_code == 200:
            # Verificar que es un PDF válido
            content = response.content
            
            # Los PDFs comienzan con %PDF-
            if content[:4] == b'%PDF':
                print(f"✅ PDF generado correctamente ({len(content)} bytes)")
                
                # Guardar archivo para inspección manual
                filename = f"test_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(content)
                print(f"📄 Archivo guardado como: {filename}")
                return True
            else:
                print(f"❌ El contenido no es un PDF válido")
                print(f"   Primeros bytes: {content[:20]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_excel_export(report_type="equipos"):
    """Prueba la exportación de Excel"""
    print(f"\n🔍 Probando exportación Excel para: {report_type}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/reportes/export/excel",
            json={"type": report_type},
            timeout=30
        )
        
        if response.status_code == 200:
            # Verificar que es un archivo Excel válido (ZIP format)
            content = response.content
            
            # Los archivos XLSX son archivos ZIP que comienzan con PK
            if content[:2] == b'PK':
                print(f"✅ Excel generado correctamente ({len(content)} bytes)")
                
                # Guardar archivo para inspección manual
                filename = f"test_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with open(filename, 'wb') as f:
                    f.write(content)
                print(f"📄 Archivo guardado como: {filename}")
                return True
            else:
                print(f"❌ El contenido no es un Excel válido")
                print(f"   Primeros bytes: {content[:20]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_dashboard():
    """Prueba que el dashboard funciona (respuesta JSON normal)"""
    print(f"\n🔍 Probando endpoint de dashboard (JSON)")
    
    try:
        response = requests.get(
            f"{API_URL}/api/reportes/dashboard",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard funciona correctamente")
            print(f"   Total equipos: {data.get('total_equipos', 'N/A')}")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBAS DE EXPORTACIÓN DE REPORTES")
    print("=" * 60)
    
    # Verificar conexión
    print(f"\n📡 Conectando a: {API_URL}")
    
    results = []
    
    # Probar dashboard (JSON)
    results.append(("Dashboard JSON", test_dashboard()))
    
    # Probar PDFs
    for report_type in ["equipos", "mantenimientos", "proveedores"]:
        results.append((f"PDF {report_type}", test_pdf_export(report_type)))
    
    # Probar Excel
    for report_type in ["equipos", "mantenimientos", "proveedores"]:
        results.append((f"Excel {report_type}", test_excel_export(report_type)))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("✨ ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revise los logs arriba.")

