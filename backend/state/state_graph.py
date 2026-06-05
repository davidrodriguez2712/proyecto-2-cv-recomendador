#from langgraph.graph import StateGraph, END, START
#from langgraph.prebuilt import tools_condition, ToolNode
from typing import TypedDict, Annotated, Literal, Sequence, Optional, List
from pydantic import BaseModel, Field, HttpUrl
from langgraph.graph.message import add_messages
from enum import Enum

class CategoriaLaboral(str, Enum):
    CONTABILIDAD = "Contabilidad y Auditoría"
    CONSULTORIA = "Consultoría y Asesoría Empresarial"
    DISENO = "Diseño y Creatividad"
    ATENCION_CLIENTE = "Atención al Cliente y Soporte"
    EDUCACION = "Educación y Capacitación"
    INGENIERIA_ELECTRICA = "Ingeniería Eléctrica y Electrónica"
    ENERGIA = "Energía y Medio Ambiente"
    FINANZAS = "Finanzas y Banca"
    SALUD = "Salud y Servicios Médicos"
    RRHH= "Recursos Humanos"
    ADMIN = "Administración"
    SERVICIOS_LEGALES = "Servicios Jurídicos y Legales"
    LOGISTICA = "Logística y Cadena de Suministro"
    MARKETING_COMUNICACIONES = "Marketing y Comunicación"
    PRODUCTO = "Gestión de Producto"
    MANUFACTURA = "Producción e Industria Manufacturera"
    GOBIERNO = "Sector Público y Gobierno"
    ARQUITECTURA = "Bienes Raíces y Arquitectura"
    VENTAS = "Ventas y Desarrollo Comercial"
    TECNOLOGIA = "Tecnología, Software e Inteligencia Artificial"
    GASTRONOMIA = "Gastronomía y Cocina"
    LIMPIEZA = "Limpieza y Mantenimiento"
    TRANSPORTE = "Transporte y Conducción"
    SEGURIDAD = "Seguridad y Vigilancia"
    CONSTRUCCION = "Construcción y Oficios"
    TURISMO = "Turismo y Hotelería"
    RETAIL = "Ventas Minoristas y Atención en Tienda"
    ESTETICA = "Cuidado Personal y Estética"
    SERVICIOS_DOMESTICOS = "Servicios Domésticos y Asistencia Familiar"

class SectorIndustria(str, Enum):
    AGRICULTURA = "Agricultura, Pesca y Ganadería"
    ALIMENTOS_BEBIDAS = "Alimentos, Bebidas y Consumo Masivo"
    AUTOMOTRIZ = "Automotriz y Transporte"
    BANCA_FINANZAS = "Banca, Finanzas y Seguros"
    CONSTRUCCION = "Construcción e Infraestructura"
    CONSULTORIA = "Consultoría y Servicios Profesionales"
    EDUCACION = "Educación y Formación"
    ENERGIA_MINERIA = "Energía, Petróleo y Minería"
    ENTRETENIMIENTO = "Entretenimiento, Medios y Deportes"
    FARMACEUTICA_SALUD = "Farmacéutica, Biotecnología y Salud"
    GOBIERNO = "Gobierno y Sector Público"
    INMOBILIARIO = "Bienes Raíces e Inmobiliario"
    LOGISTICA_TRANSPORTE = "Logística, Transporte y Comercio Exterior"
    MANUFACTURA = "Manufactura e Industria"
    MARKETING_PUBLICIDAD = "Marketing, Publicidad y Comunicación"
    ONG = "Organizaciones Sin Fines de Lucro (ONG)"
    RETAIL = "Retail, Comercio y Ventas Minoristas"
    SERVICIOS_TECNICOS = "Servicios Técnicos e Ingeniería"
    TECNOLOGIA = "Tecnología, Software e Inteligencia Artificial"
    TELECOMUNICACIONES = "Telecomunicaciones y Conectividad"
    TEXTIL_MODA = "Textil, Moda y Diseño"
    TURISMO_HOTELERIA = "Turismo, Hotelería y Restauración"
    MEDIO_AMBIENTE = "Medio Ambiente y Sostenibilidad"
    LEGAL = "Legal y Servicios Jurídicos"
    SEGURIDAD_DEFENSA = "Seguridad, Defensa y Vigilancia"

class Educacion(BaseModel):
    institucion: str = Field(..., description="Nombre de la institución educativa")
    carrera: str = Field(..., description="Nombre de la carrera o especialización")
    nivel: str = Field(..., description="Nivel académico (Egresado, Bachiller, Licenciatura, etc.)")
    periodo: str = Field(..., description="Periodo de estudio, por ejemplo '2015-2020'")
    estado: Optional[str] = Field("", description="Estado de finalización (Completo, En curso)")
    rendimiento: Optional[str] = Field("", description="Rendimiento académico, ej. 'Tercio superior'")

class ExperienciaLaboral(BaseModel):
    puesto: str = Field(..., description="Título del puesto desempeñado")
    empresa: str = Field(..., description="Nombre de la empresa")
    url_empresa: Optional[str] = Field("", description="URL de la empresa")
    periodo: str = Field(..., description="Periodo de trabajo, ej. 'Marzo 2024 – Actualidad'")
    descripcion: Optional[str] = Field("", description="Descripción de responsabilidades y funciones")
    logros: Optional[str] = Field("", description="Logros o resultados alcanzados en el puesto")
    anos_experiencia_empleo: Optional[float] = Field("", description="Años de experiencia en el puesto")
    nivel: Optional[str] = Field("", description="Nivel del puesto, ej. Analista, Ejecutivo")

class Idioma(BaseModel):
    idioma: str = Field(..., description="Nombre del idioma")
    nivel: str = Field(..., description="Nivel de dominio del idioma, ej. Nativo, Intermedio, Avanzado")

class NivelSalarial(BaseModel):
    min: Optional[float] = Field(0, description="Salario mínimo esperado")
    max: Optional[float] = Field(0, description="Salario máximo esperado")
    moneda: Optional[str] = Field("PEN", description="Moneda del salario esperado")


class CVData(BaseModel):
    """Formato estructurado del CV del usuario"""
    nombre_completo: str = Field(..., description="Nombre completo del candidato")
    dni: Optional[int] = Field("", description="Número de documento de identidad")
    telefono: Optional[str] = Field("", description="Número de teléfono de contacto")
    email: Optional[str] = Field("", description="Correo electrónico de la persona")
    linkedin: Optional[str] = Field("", description="URL de perfil de LinkedIn")
    portfolio_blog: Optional[str] = Field("", description="URL de portafolio o blog personal")
    fecha_extraccion: Optional[str] = Field("", description="Fecha de extracción del CV")
    titulo_profesional: Optional[str] = Field("", description="Título profesional del candidato")
    educacion: Optional[List[Educacion]] = Field([], description="Lista de formaciones académicas")
    certificaciones: Optional[List[str]] = Field([], description="Lista de certificaciones obtenidas")
    experiencia_laboral: Optional[List[ExperienciaLaboral]] = Field([], description="Lista de experiencias laborales")
    industrias_experiencia: Optional[List[SectorIndustria]] = Field([], description="Industria a la que pertenece la empresa por cada experiencia laboral")
    categorias_laborales: Optional[List[CategoriaLaboral]] = Field([], description= "Lista de categorías laborales a las que pertenece el perfil de acuerdo a cada experiencia laboral")
    habilidades_tecnicas: Optional[List[str]] = Field([], description="Lista de habilidades técnicas y herramientas")
    idiomas: Optional[List[Idioma]] = Field([], description="Idiomas y nivel de dominio")
    anos_experiencia_total: Optional[float] = Field("", description="Años totales de experiencia laboral, se debería sumar el tiempo de cada experiencia laboral")
    actividades_extracurriculares: Optional[List[str]] = Field([], description="Actividades extracurriculares o liderazgo")
    ubicacion_preferida: Optional[str] = Field("", description="Ubicación geográfica preferida para trabajar")
    modalidad_preferida: Optional[str] = Field("", description="Modalidad de trabajo preferida, ej. Híbrido o Remoto")
    nivel_salarial_esperado: Optional[NivelSalarial] = Field(NivelSalarial(), description="Rango salarial esperado")
    keywords_perfil: Optional[List[str]] = Field([], description="Palabras clave relacionadas con el perfil del candidato")
    texto_embedding: Optional[str] = Field("", description="Texto narrativo enriquecido para embeddings o búsqueda vectorial")
    
class EmpleosData(BaseModel):
    """Formato estructurado del feedback fit CV vs la oferta de empleo comparada"""
    nombre_empleo: str = Field(..., description="Es el nombre de la oferta de empleo")
    modalidad_trabajo: Optional[str] = Field("", description= "Es la modalidad de trabajo del empleo como Full-time o Part-time")
    ubicacion: Optional[str] = Field("", description= "Es la ubicación donde se llevará a cabo el empleo")
    seniority: str = Field(..., description= "Es el seniority del puesto de empleo, por ejemplo son Senior, Semisenior, Junior, etc.")
    anos_experiencia: Optional[int] = Field("", description= "Son los años de experiencia requeridos en el puesto de empleo")
    experiencia_relevante: Optional[str] = Field("", description= "Este campo debe responder a la pregunta por qué el empleo es buen match para el usuario (de acuerdo a su cv) a nivel de experiencia laboral, que estan ligadas a las funciones del puesto.")
    seniority_relevante: Optional[str] = Field("", description= "Este campo debe responder a la pregunta por qué el empleo es buen match para el usuario (de acuerdo a su cv) a nivel de seniority/años de experiencia.")
    educacion_relevante: Optional[str] = Field("", description= "Este campo debe responder a la pregunta por qué el empleo es buen match para el usuario (de acuerdo a su cv) a nivel de educación.")
    skills_relevante: Optional[str] = Field("", description= "Este campo debe responder a la pregunta por qué el empleo es buen match para el usuario (de acuerdo a su cv) a nivel de skills técnicos.")
    url: str = Field(..., description= "Es la URL del puesto de empleo.")
    puntuacion_match: float = Field(..., description= "Es la puntuación dado por la búsqueda semántica del CV usuario vs la oferta de empleo")

class ListaEmpleosData(BaseModel):
    """Formato estructurado para las listas de la clase EmpleosData"""
    lista_empleos_data: List[EmpleosData]

class State(TypedDict):
    messages: str
    cv_object: dict
    cv_file_pdf: str
    cv_data: CVData
    cv_metadata: dict
    cv_texto: str
    id_cv: str
    cv_resumen: str
    cv_vector: List
    cv_empleos_recomendados: List[str] #"Son los empleos recomendados de acuerdo a la búsqueda por similitud"]
    cv_feedback: ListaEmpleosData
    respuesta_empleos_recomendados: str

#CVData.educacion[0].carrera








