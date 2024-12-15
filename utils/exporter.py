from typing import List, Dict, Optional
import os
from datetime import datetime
import zipfile
import tempfile
from config import UIConfig

class PaperExporter:
    """论文导出器"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.encoding = UIConfig.FILE_ENCODING
    
    def export_summary(self, summary: Dict) -> str:
        """导出单个总结为Markdown文件"""
        filename = f"{summary['filename']}.md"
        filepath = os.path.join(self.temp_dir, filename)
        
        with open(filepath, 'w', encoding=self.encoding) as f:
            f.write(summary['summary'])
        
        if summary.get('mindmap'):
            img_filename = f"{summary['filename']}_mindmap.png"
            img_filepath = os.path.join(self.temp_dir, img_filename)
            with open(img_filepath, 'wb') as f:
                f.write(summary['mindmap'])
        
        return filepath
    
    def export_batch(self, summaries: List[Dict]) -> bytes:
        """批量导出总结为ZIP文件"""
        try:
            # 创建临时ZIP文件
            zip_path = os.path.join(self.temp_dir, 'summaries.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加每个总结文件
                for summary in summaries:
                    md_path = self.export_summary(summary)
                    arcname = os.path.basename(md_path)
                    zipf.write(md_path, arcname)
                    
                    if summary.get('mindmap'):
                        img_filename = f"{summary['filename']}_mindmap.png"
                        img_filepath = os.path.join(self.temp_dir, img_filename)
                        zipf.write(img_filepath, img_filename)
                    
                # 添加README文件
                readme_content = self._generate_readme(summaries)
                readme_path = os.path.join(self.temp_dir, 'README.md')
                with open(readme_path, 'w', encoding=self.encoding) as f:
                    f.write(readme_content)
                zipf.write(readme_path, 'README.md')
            
            # 读取ZIP文件内容
            with open(zip_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")
            
        finally:
            # 清理临时文件
            self._cleanup()
    
    def _generate_readme(self, summaries: List[Dict]) -> str:
        """生成README文件"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""# 论文总结导出
        
## 导出信息
- 导出时间：{now}
- 文件数量：{len(summaries)}
- 处理模式：{summaries[0].get('mode', '未知')}
- 文件编码：{self.encoding}

## 文件列表
"""
        
        for summary in summaries:
            content += f"- {summary['filename']}\n"
            
        content += """
## 说明
- 所有文件均为Markdown格式
- 每个文件包含一篇论文的总结
- 总结包含研究背景、方法、结果等关键信息
- 对应的思维导图以PNG格式保存（文件名：论文名_mindmap.png）
"""
        
        return content
    
    def _cleanup(self):
        """清理临时文件"""
        try:
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                if os.path.isfile(filepath):
                    os.unlink(filepath)
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")