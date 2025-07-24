#!/usr/bin/env python3
"""
Standalone Extraction Testing Script
Test what data is extracted from documents before embedding conversion
"""

import os
import sys
import json
from typing import Dict, Any, List
from pathlib import Path
import streamlit as st

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from processors.file_processor import PureLLMFileProcessor
from utils.config import Config

class ExtractionTester:
    """Test extraction capabilities of the system"""
    
    def __init__(self):
        # Load configuration
        Config.ensure_directories()
        
        # Check API keys
        is_valid, message = Config.validate_required_keys()
        if not is_valid:
            print(f"❌ API Configuration Error: {message}")
            print("Please check your .env file")
            sys.exit(1)
        
        # Initialize processor
        self.processor = PureLLMFileProcessor(Config.GROQ_API_KEY)
        print("✅ Extraction Tester initialized successfully")
    
    def test_file_extraction(self, file_path: str, output_dir: str = "extraction_results") -> Dict[str, Any]:
        """Test extraction on a single file"""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        print(f"\n🔍 Testing extraction on: {os.path.basename(file_path)}")
        
        # Create a mock uploaded file object
        class MockUploadedFile:
            def __init__(self, file_path):
                self.name = os.path.basename(file_path)
                with open(file_path, 'rb') as f:
                    self._content = f.read()
                self.size = len(self._content)
                self._position = 0
            
            def read(self):
                content = self._content[self._position:]
                self._position = len(self._content)
                return content
        
        mock_file = MockUploadedFile(file_path)
        
        # Process the file
        try:
            result = self.processor.process_file(mock_file, force_vision=True)
            
            # Save results
            os.makedirs(output_dir, exist_ok=True)
            
            filename_base = os.path.splitext(os.path.basename(file_path))[0]
            
            # Save extracted text
            with open(os.path.join(output_dir, f"{filename_base}_extracted_text.txt"), 'w', encoding='utf-8') as f:
                f.write(result.get('text', 'No text extracted'))
            
            # Save raw data if available
            if 'raw_text' in result:
                with open(os.path.join(output_dir, f"{filename_base}_raw_text.txt"), 'w', encoding='utf-8') as f:
                    f.write(result['raw_text'])
            
            # Save metadata
            with open(os.path.join(output_dir, f"{filename_base}_metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(result.get('metadata', {}), f, indent=2)
            
            # Save vision analyses if available
            if 'vision_analyses' in result:
                with open(os.path.join(output_dir, f"{filename_base}_vision_analysis.json"), 'w', encoding='utf-8') as f:
                    json.dump(result['vision_analyses'], f, indent=2)
            
            # Save text analysis if available
            if 'text_analysis' in result:
                with open(os.path.join(output_dir, f"{filename_base}_text_analysis.txt"), 'w', encoding='utf-8') as f:
                    f.write(result['text_analysis'].get('analysis', 'No text analysis'))
            
            print(f"✅ Extraction completed for {os.path.basename(file_path)}")
            print(f"📁 Results saved to: {output_dir}")
            
            return {
                "success": True,
                "file": file_path,
                "extracted_length": len(result.get('text', '')),
                "has_vision_analysis": 'vision_analyses' in result,
                "has_text_analysis": 'text_analysis' in result,
                "metadata": result.get('metadata', {}),
                "output_dir": output_dir
            }
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def test_directory_extraction(self, directory_path: str, output_dir: str = "extraction_results") -> Dict[str, Any]:
        """Test extraction on all files in a directory"""
        if not os.path.exists(directory_path):
            return {"error": f"Directory not found: {directory_path}"}
        
        print(f"\n📁 Testing extraction on directory: {directory_path}")
        
        supported_extensions = ['.pdf', '.csv', '.xlsx', '.xls', '.txt', '.docx', '.png', '.jpg', '.jpeg', '.las', '.tiff', '.tif']
        
        files_to_process = []
        for ext in supported_extensions:
            files_to_process.extend(Path(directory_path).glob(f"*{ext}"))
            files_to_process.extend(Path(directory_path).glob(f"*{ext.upper()}"))
        
        if not files_to_process:
            return {"error": "No supported files found in directory"}
        
        print(f"Found {len(files_to_process)} files to process")
        
        results = []
        for file_path in files_to_process:
            result = self.test_file_extraction(str(file_path), output_dir)
            results.append(result)
        
        # Summary
        successful = len([r for r in results if 'success' in r])
        failed = len(results) - successful
        
        summary = {
            "total_files": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
            "output_dir": output_dir
        }
        
        print(f"\n📊 Summary: {successful}/{len(results)} files processed successfully")
        
        return summary
    
    def analyze_extraction_quality(self, output_dir: str = "extraction_results") -> Dict[str, Any]:
        """Analyze the quality of extractions"""
        if not os.path.exists(output_dir):
            return {"error": f"Output directory not found: {output_dir}"}
        
        print(f"\n🔍 Analyzing extraction quality in: {output_dir}")
        
        analysis = {
            "files_analyzed": 0,
            "average_text_length": 0,
            "files_with_vision": 0,
            "files_with_text_analysis": 0,
            "quality_metrics": {}
        }
        
        text_files = list(Path(output_dir).glob("*_extracted_text.txt"))
        
        total_length = 0
        for text_file in text_files:
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_length += len(content)
                    analysis["files_analyzed"] += 1
                
                # Check for corresponding vision analysis
                vision_file = text_file.parent / text_file.name.replace("_extracted_text.txt", "_vision_analysis.json")
                if vision_file.exists():
                    analysis["files_with_vision"] += 1
                
                # Check for text analysis
                text_analysis_file = text_file.parent / text_file.name.replace("_extracted_text.txt", "_text_analysis.txt")
                if text_analysis_file.exists():
                    analysis["files_with_text_analysis"] += 1
                
            except Exception as e:
                print(f"⚠️ Error analyzing {text_file}: {e}")
        
        if analysis["files_analyzed"] > 0:
            analysis["average_text_length"] = total_length / analysis["files_analyzed"]
        
        analysis["quality_metrics"] = {
            "vision_coverage": analysis["files_with_vision"] / max(analysis["files_analyzed"], 1) * 100,
            "text_analysis_coverage": analysis["files_with_text_analysis"] / max(analysis["files_analyzed"], 1) * 100,
            "average_extraction_size": analysis["average_text_length"]
        }
        
        print(f"📈 Quality Analysis:")
        print(f"   Files analyzed: {analysis['files_analyzed']}")
        print(f"   Vision coverage: {analysis['quality_metrics']['vision_coverage']:.1f}%")
        print(f"   Text analysis coverage: {analysis['quality_metrics']['text_analysis_coverage']:.1f}%")
        print(f"   Average extraction size: {analysis['average_extraction_size']:.0f} characters")
        
        return analysis
    
    def interactive_test(self):
        """Interactive testing interface"""
        print("\n" + "="*60)
        print("🧪 SMART GEOLOGICAL RAG - EXTRACTION TESTER")
        print("="*60)
        
        while True:
            print("\nChoose an option:")
            print("1. Test single file extraction")
            print("2. Test directory extraction")
            print("3. Analyze extraction quality")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                file_path = input("Enter file path: ").strip()
                result = self.test_file_extraction(file_path)
                if 'error' not in result:
                    print(f"✅ Success! Extracted {result['extracted_length']} characters")
                else:
                    print(f"❌ {result['error']}")
            
            elif choice == '2':
                dir_path = input("Enter directory path: ").strip()
                result = self.test_directory_extraction(dir_path)
                if 'error' not in result:
                    print(f"✅ Processed {result['successful']}/{result['total_files']} files successfully")
                else:
                    print(f"❌ {result['error']}")
            
            elif choice == '3':
                output_dir = input("Enter output directory (default: extraction_results): ").strip()
                if not output_dir:
                    output_dir = "extraction_results"
                result = self.analyze_extraction_quality(output_dir)
                if 'error' not in result:
                    print("✅ Quality analysis completed")
                else:
                    print(f"❌ {result['error']}")
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == 'file' and len(sys.argv) > 2:
            tester = ExtractionTester()
            result = tester.test_file_extraction(sys.argv[2])
            print(json.dumps(result, indent=2))
        
        elif sys.argv[1] == 'dir' and len(sys.argv) > 2:
            tester = ExtractionTester()
            result = tester.test_directory_extraction(sys.argv[2])
            print(json.dumps(result, indent=2))
        
        elif sys.argv[1] == 'analyze':
            tester = ExtractionTester()
            output_dir = sys.argv[2] if len(sys.argv) > 2 else "extraction_results"
            result = tester.analyze_extraction_quality(output_dir)
            print(json.dumps(result, indent=2))
        
        else:
            print("Usage:")
            print("  python extraction_tester.py file <file_path>")
            print("  python extraction_tester.py dir <directory_path>")
            print("  python extraction_tester.py analyze [output_dir]")
    
    else:
        # Interactive mode
        tester = ExtractionTester()
        tester.interactive_test()

if __name__ == "__main__":
    main()
