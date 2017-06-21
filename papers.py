import os
from pathlib import Path


class Papers (dict):
    papers = {}

    def __init__(self, papers_path):
        super().__init__()
        self.path = Path(papers_path)
        self.load_papers()

    def load_papers(self):
        if not self.path.exists():
            self.path.mkdir()
            pth = self.path / Path('note.txt')
            pth.touch()

        files = [x for x in self.path.glob("*") if x.is_file()]
        for i in files:
            p = Paper()
            p.text = i.read_text()
            p.name = i.name
            self[i.name] = (p)

    def add_paper(self, name):
        p = Paper()
        p.name = name
        pth = self.path / Path(name)
        pth.touch()
        self[name] = p

    def rename_paper(self, name, rename):
        p = self[name]
        pth = self.path / Path(name)
        new_pth = self.path / Path(rename)
        pth.rename(new_pth)
        del self[name]
        self[rename] = p

    def delete_paper(self, name):
        del self[name]
        os.remove(self.path / Path(name))

    def save_paper(self, name):
        p = self.path / Path(name)
        p.write_text(self[name].text)

    def paper_exists(self, name):
        p = self.path / Path(name)
        return p.exists()


class Paper:
    text = ""
    name = ""
