import os
import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from pathlib import Path


class Papers (dict):

    def __init__(self, papers_path):
        super().__init__()
        self.path = Path(papers_path)
        self.initPath()
        self.getSalt()

    def initPath(self):
        if not self.path.exists():
            self.path.mkdir()

    def setPassword(self, pwd):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32,
                         salt=self.salt,
                         iterations=1000,
                         backend=default_backend())
        self.key = base64.urlsafe_b64encode(kdf.derive(pwd.encode()))
        self.fernet = Fernet(self.key)

    def getSalt(self):
        pth = self.path / Path('salt')
        if pth.exists():
            self.salt = pth.read_bytes()
        else:
            self.salt = os.urandom(16)
            salt64 = base64.urlsafe_b64encode(self.salt)
            pth.write_bytes(salt64)

    def load_papers(self):
        files = [x for x in self.path.glob("*") if x.is_file()]
        for i in files:
            if i.name != 'salt':
                p = Paper()
                btext = i.read_bytes()
                try:
                    p.text = self.fernet.decrypt(btext).decode()
                    p.name = i.name
                    self[i.name] = (p)
                except InvalidToken:
                    raise ValueError("Invalid Password")

    def add_paper(self, name):
        p = Paper()
        p.name = name
        pth = self.path / Path(name)
        self[name] = p
        self.save_paper(name)

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
        btext = self[name].text.encode()
        cbtext = self.fernet.encrypt(btext)
        p.write_bytes(cbtext)
        # p.write_text(self[name].text)

    def paper_exists(self, name):
        p = self.path / Path(name)
        return p.exists()


class Paper:
    text = ""
    name = ""
