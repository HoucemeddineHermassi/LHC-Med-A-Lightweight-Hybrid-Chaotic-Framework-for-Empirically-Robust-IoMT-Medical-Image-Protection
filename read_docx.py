import zipfile
import xml.etree.ElementTree as ET
import sys

def read_docx(file_path):
    """Extract text from a DOCX file."""
    with zipfile.ZipFile(file_path) as docx:
        xml_content = docx.read('word/document.xml')
        tree = ET.XML(xml_content)
        
        # Namespace for Word documents
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        paragraphs = []
        for paragraph in tree.findall('.//w:p', ns):
            texts = []
            for node in paragraph.findall('.//w:t', ns):
                if node.text:
                    texts.append(node.text)
            if texts:
                paragraphs.append(''.join(texts))
        
        return '\n'.join(paragraphs)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = r"d:\Atelier HDR\ENCRYPT MEDICAL\paper\action-plan3.docx"
    
    content = read_docx(docx_path)
    
    # Write to file with UTF-8 encoding
    import os
    base_name = os.path.basename(docx_path).replace('.docx', '')
    output_path = os.path.join(r"d:\Atelier HDR\ENCRYPT MEDICAL\enhanced_encryption", f"{base_name}_content.txt")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Content extracted to: {output_path}")
