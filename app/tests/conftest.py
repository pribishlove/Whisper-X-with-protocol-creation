import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root) 