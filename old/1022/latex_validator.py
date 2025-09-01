import re
from typing import Tuple, List, Dict, Optional

class LatexValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_tex_file(self, file_path: str) -> Tuple[bool, Dict[str, any]]:
        """
        Valida un archivo LaTeX según los requisitos especificados
        
        Args:
            file_path: Ruta al archivo .tex a validar
            
        Returns:
            Tuple[bool, Dict]: (True/False si es válido, diccionario con metadatos y errores)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Preprocesamiento: eliminar comentarios
            content = self._remove_comments(content)
            
            # Inicializar estado de validación
            validation_state = {
                'is_valid': True,
                'metadata': {},
                'errors': [],
                'warnings': []
            }
            
            # Verificar elementos obligatorios
            self._check_required_elements(content, validation_state)
            
            # Extraer metadatos
            self._extract_metadata(content, validation_state)
            
            # Verificar paquetes (opcional)
            self._check_packages(content, validation_state)
            
            # Determinar si es válido (sin errores críticos)
            validation_state['is_valid'] = not bool(validation_state['errors'])
            
            return validation_state['is_valid'], validation_state
            
        except Exception as e:
            return False, {
                'is_valid': False,
                'errors': [f"Error al leer el archivo: {str(e)}"],
                'warnings': [],
                'metadata': {}
            }
    
    def _remove_comments(self, content: str) -> str:
        """Elimina comentarios de LaTeX (líneas que comienzan con %)"""
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Ignorar líneas que son puramente comentarios
            if not line.strip().startswith('%'):
                # Eliminar partes comentadas al final de las líneas
                uncommented = line.split('%')[0]
                cleaned_lines.append(uncommented)
        return '\n'.join(cleaned_lines)
    
    def _check_required_elements(self, content: str, state: Dict):
        """Verifica la presencia de elementos obligatorios"""
        required_elements = [
            (r'\\documentclass\[.*\]\{baaa\}', 'documentclass', 'Debe usar el estilo "baaa" en \\documentclass{}'),
            (r'\\title\{.*\}', 'title', 'No se encontró el comando \\title{}'),
            (r'\\author\{.*\}', 'authors', 'No se encontró el comando \\author{}'),
            (r'\\keywords\{.*\}', 'keywords', 'No se encontró el comando \\keywords{}'),
            (r'\\begin\{document\}', 'begin_document', 'No se encontró \\begin{document}'),
            (r'\\end\{document\}', 'end_document', 'No se encontró \\end{document}'),
            (r'\\maketitle', 'maketitle', 'No se encontró el comando \\maketitle'),
            (r'\\abstract\{.*\}', 'abstract', 'No se encontró el comando \\abstract{}'),
            (r'\\institute\{.*\}', 'institute', 'No se encontró el comando \\institute{}'),
            (r'\\contact\{.*\}', 'email', 'No se encontró el comando \\contact{} (email)'),
            (r'\\bibliographystyle\{baaa\}', 'biblio_style', 'No se encontró \\bibliographystyle{baaa}'),
            (r'\\bibliography\{.*\}', 'bibliography', 'No se encontró el comando \\bibliography{}'),
        ]
        
        for pattern, key, error_msg in required_elements:
            if not re.search(pattern, content):
                state['errors'].append(error_msg)
    
    def _extract_metadata(self, content: str, state: Dict):
        """Extrae metadatos del documento LaTeX"""
        metadata = {}
        
        # Título
        title_match = re.search(r'\\title\{(.*?)\}', content)
        if title_match:
            metadata['title'] = self._clean_latex(title_match.group(1))
        
        # Autores (manejo más complejo por posibles institutos)
        author_matches = re.finditer(r'\\author\{(.*?)\}', content, re.DOTALL)
        if author_matches:
            authors_content = next(author_matches).group(1)
            # Extraer autores e instituciones
            authors = []
            for author_part in re.split(r'\\inst\{.*?\}', authors_content):
                if author_part.strip():
                    authors.append(self._clean_latex(author_part.strip()))
            metadata['authors'] = authors
        
        # Palabras clave
        keywords_match = re.search(r'\\keywords\{(.*?)\}', content)
        if keywords_match:
            metadata['keywords'] = [kw.strip() for kw in keywords_match.group(1).split(',')]
        
        # Abstract
        abstract_match = re.search(r'\\abstract\{(.*?)\}', content, re.DOTALL)
        if abstract_match:
            metadata['abstract'] = self._clean_latex(abstract_match.group(1))
        
        # Instituciones
        institute_match = re.search(r'\\institute\{(.*?)\}', content)
        if institute_match:
            metadata['institute'] = self._clean_latex(institute_match.group(1))
        
        # Email
        email_match = re.search(r'\\contact\{(.*?)\}', content)
        if email_match:
            metadata['email'] = email_match.group(1).strip()
        
        # Figuras
        figures = re.findall(r'\\includegraphics(?:\[.*?\])?\{(.*?)\}', content)
        metadata['figures'] = figures
        
        # Bibliografía
        biblio_match = re.search(r'\\bibliography\{(.*?)\}', content)
        if biblio_match:
            metadata['bibliography'] = biblio_match.group(1).strip()
        
        state['metadata'] = metadata
    
    def _check_packages(self, content: str, state: Dict):
        """Verifica paquetes recomendados (opcional)"""
        recommended_packages = [
            ('hyperref', r'\\usepackage(?:\[.*?\])?\{hyperref\}'),
            ('natbib', r'\\usepackage(?:\[.*?\])?\{natbib\}'),
            ('caption', r'\\usepackage(?:\[.*?\])?\{caption\}'),
        ]
        
        for pkg, pattern in recommended_packages:
            if not re.search(pattern, content):
                state['warnings'].append(f'Paquete recomendado no encontrado: {pkg}')
    
    def _clean_latex(self, text: str) -> str:
        """Limpia texto LaTeX quitando comandos comunes"""
        # Eliminar comandos simples \comando
        text = re.sub(r'\\[a-zA-Z]+\s*', '', text)
        # Eliminar llaves {}
        text = re.sub(r'[\{\}]', '', text)
        # Eliminar espacios múltiples
        text = ' '.join(text.split())
        return text.strip()

# Ejemplo de uso
if __name__ == "__main__":
    validator = LatexValidator()
    is_valid, result = validator.validate_tex_file("ejemplo.tex")
    
    print(f"Archivo válido: {'Sí' if is_valid else 'No'}")
    print("\nMetadatos encontrados:")
    for key, value in result['metadata'].items():
        print(f"{key}: {value}")
    
    if result['errors']:
        print("\nErrores encontrados:")
        for error in result['errors']:
            print(f"- {error}")
    
    if result['warnings']:
        print("\nAdvertencias:")
        for warning in result['warnings']:
            print(f"- {warning}")