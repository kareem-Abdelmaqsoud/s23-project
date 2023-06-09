"""A class that returns citation information of a particular paper"""

import base64
import time
import requests
import matplotlib.pyplot as plt
from IPython.core.pylabtools import print_figure
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


class Works:
    """A works class that returns the RIS and BIBTEX"""

    def __init__(self, oaid):
        """Initalize variables"""
        self.oaid = oaid
        self.req = requests.get(f"https://api.openalex.org/works/{oaid}")
        self.data = self.req.json()

    def __str__(self):
        """Returns a string"""
        return "str"

    def __repr__(self):
        """Returns a representation"""
        _authors = [au["author"]["display_name"] for au in self.data["authorships"]]
        if len(_authors) == 1:
            authors = _authors[0]
        else:
            authors = ", ".join(_authors[0:-1]) + " and" + _authors[-1]

        title = self.data["title"]

        volume = self.data["biblio"]["volume"]

        issue = self.data["biblio"]["issue"]
        if issue is None:
            issue = ", "
        else:
            issue = ", " + issue

        pages = "-".join(
            [self.data["biblio"]["first_page"], self.data["biblio"]["last_page"]]
        )
        year = self.data["publication_year"]
        citedby = self.data["cited_by_count"]

        o_a = self.data["id"]
        s_s = "{}, {}, {}{}{}, ({}), {}. cited by: {}. {}".format(
            authors, title, volume, issue, pages, year, self.data["doi"], citedby, o_a
        )
        return s_s

    def _repr_markdown_(self):
        """Returns markdown representation"""
        _authors = [
            f'[{au["author"]["display_name"]}]({au["author"]["id"]})'
            for au in self.data["authorships"]
        ]
        if len(_authors) == 1:
            authors = _authors[0]
        else:
            authors = ", ".join(_authors[0:-1]) + " and " + _authors[-1]
        dictionary = {
            "title": self.data["title"],
            "volume": self.data["biblio"]["volume"],
            "pages": "-".join(
                [self.data["biblio"]["first_page"], self.data["biblio"]["last_page"]]
            ),
            "year": self.data["publication_year"],
            "citedby": self.data["cited_by_count"],
            "o_a": self.data["id"],
        }
        journal = f"[{self.data['host_venue']['display_name']}]({self.data['host_venue']['id']})"
        issue = self.data["biblio"]["issue"]
        if issue is None:
            issue = ", "
        else:
            issue = ", " + issue

        # Citation counts by year
        years = [e["year"] for e in self.data["counts_by_year"]]
        counts = [e["cited_by_count"] for e in self.data["counts_by_year"]]

        fig, a_x = plt.subplots()
        a_x.bar(years, counts)
        a_x.set_xlabel("year")
        a_x.set_ylabel("citation count")
        data = print_figure(fig, "png")  # save figure in string
        plt.close(fig)

        b64 = base64.b64encode(data).decode("utf8")
        citefig = f"![img](data:image/png;base64,{b64})"
        s_s = (
            "{}, *{}*, **{}**, {}{}{}, ({}), {}. cited by: {}. [Open Alex]({})".format(
                authors,
                dictionary["title"],
                journal,
                dictionary["volume"],
                issue,
                dictionary["pages"],
                dictionary["year"],
                self.data["doi"],
                dictionary["citedby"],
                dictionary["o_a"],
            )
        )
        s_s += "<br>" + citefig
        return s_s

    @property
    def ris(self):
        """Returns RIS entry"""
        fields = []
        if self.data["type"] == "journal-article":
            fields += ["TY  - JOUR"]
        else:
            raise Exception("Unsupported type {self.data['type']}")

        for author in self.data["authorships"]:
            fields += [f'AU  - {author["author"]["display_name"]}']

        fields += [f'PY  - {self.data["publication_year"]}']
        fields += [f'TI  - {self.data["title"]}']
        fields += [f'JO  - {self.data["host_venue"]["display_name"]}']
        fields += [f'VL  - {self.data["biblio"]["volume"]}']

        if self.data["biblio"]["issue"]:
            fields += [f'IS  - {self.data["biblio"]["issue"]}']

        fields += [f'SP  - {self.data["biblio"]["first_page"]}']
        fields += [f'EP  - {self.data["biblio"]["last_page"]}']
        fields += [f'DO  - {self.data["doi"]}']
        fields += ["ER  -"]

        ris = "\n".join(fields)

        return ris

    def related_works(self):
        """Returns a list of related works"""
        rworks = []
        for rw_url in self.data["related_works"]:
            r_w = Works(rw_url)
            rworks += [r_w]
            time.sleep(0.101)
        return rworks

    def citing_works(self):
        """Returns a list of citing works"""
        citations_json = requests.get(self.data["cited_by_api_url"]).json()
        citing_papers = citations_json["results"]
        for i, paper in enumerate(citing_papers):
            print(f'{i+1:2d}- Title: {paper["title"]}')
            print("Doi:", paper["doi"])
            print("Publication_year:", paper["publication_year"])
            print("\n")

    def references(self):
        """Returns a list of references"""
        for i, url in enumerate(self.data["referenced_works"]):
            time.sleep(0.101)
            paper_id = url[21:]
            referenced_paper = requests.get(
                f"https://api.openalex.org/works/{paper_id}"
            ).json()
            print(f'{i+1:2d}- Title:{referenced_paper["title"]}')
            print("Doi:", referenced_paper["doi"])
            print("Publication_year:", referenced_paper["publication_year"])
            print("\n")

    @property
    def bibtex(self):
        """Returns a bibtex entry"""
        year = self.data["publication_year"]
        _authors = [au["author"]["display_name"] for au in self.data["authorships"]]
        if len(_authors) == 1:
            authors = _authors[0]
        else:
            authors = ", ".join(_authors[0:-1]) + " and " + _authors[-1]

        title = self.data["title"]

        journal = self.data["host_venue"]["display_name"]
        volume = self.data["biblio"]["volume"]
        issue = self.data["biblio"]["issue"]
        if issue is None:
            issue = ", "
        else:
            issue = ", " + issue

        pages = "-".join(
            [
                self.data["biblio"].get("first_page", "") or "",
                self.data["biblio"].get("last_page", "") or "",
            ]
        )

        d_b = BibDatabase()
        d_b.entries = [
            {
                "journal": journal,
                "pages": str(pages),
                "title": title,
                "year": str(year),
                "volume": str(volume),
                "ID": authors.split()[-1] + str(year),
                "author": authors,
                "doi": self.data["doi"],
                "ENTRYTYPE": self.data["type"],
            }
        ]
        writer = BibTexWriter()
        writer.indent = "    "  # indent entries with 4 spaces instead of one
        writer.comma_first = False  # place the comma at the beginning of the line
        return writer.write(d_b)
