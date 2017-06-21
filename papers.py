import os
import pathlib

papers_path = "./papers"


class Papers (dict):
    papers = {}

    def __init__(self):
        self.path = pathlib.Path(papers_path)
        self.load_papers()

    def load_papers(self):
        files = [x for x in self.path.glob("*") if x.is_file()]
        for i in files:
            p = Paper()
            p.text = i.read_text()
            p.name = i.name
            self[i.name] = (p)

    def add_paper(self, name):
        p = Paper()
        p.name = name
        pth = pathlib.Path(papers_path) / pathlib.Path(name)
        pth.touch()
        self[name] = p

    def rename_paper(self, name, rename):
        p = self[name]
        pth = pathlib.Path(papers_path) / pathlib.Path(name)
        new_pth = pathlib.Path(papers_path) / pathlib.Path(rename)
        pth.rename(new_pth)
        del self[name]
        self[rename] = p

    def delete_paper(self, name):
        del self[name]
        os.remove(pathlib.Path(papers_path) / pathlib.Path(name))

    def save_paper(self, name):
        p = pathlib.Path(papers_path) / pathlib.Path(name)
        p.write_text(self[name].text)

    def paper_exists(self, name):
        p = pathlib.Path(papers_path) / pathlib.Path(name)
        return p.exists()


class Paper:
    text = ""
    name = ""
