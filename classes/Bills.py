class Bills:
    """A class that is used to build the Bills"""
    def __init__(self, digest):
        self.title = digest.get("title")
        self.short_title = digest.get("shortTitle")
        self.collection_code = digest.get("collectionCode")
        self.collection_name = digest.get("collectionName")
        self.category = digest.get("category")
        self.date_issued = digest.get("dateIssued")
        self.details_link = digest.get("detailsLink")
        self.package_ID = digest.get("packageId")
        self.download = digest.get("download")
        self.related = digest.get("related")
        self.branch = digest.get("branch")
        self.pages = digest.get("pages")
        self.government_author_1 = digest.get("governmentAuthor1")
        self.government_author_2 = digest.get("governmentAuthor2")
        self.SuDoc_class_number = digest.get("suDocClassNumber")
        self.bill_type = digest.get("billType")
        self.congress = digest.get("congress")
        self.origin_chamber = digest.get("originChamber")
        self.current_chamber = digest.get("currentChamber")
        self.session = digest.get("session")
        self.bill_number = digest.get("billNumber")
        self.bill_version = digest.get("billVersion")
        self.is_appropriation = digest.get("isAppropriation")
        self.is_private = digest.get("isPrivate")
        self.publisher = digest.get("publisher")
        self.committees = digest.get("committees")
        self.members = digest.get("members")
        self.other_identifier = digest.get("otherIdentifier")
        self.references = digest.get("references")
        self.last_modified = digest.get("lastModified")