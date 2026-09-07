"""Parser for the server-rendered Bundestag member biography page."""

import json
import re
from dataclasses import dataclass
from datetime import date
from hashlib import sha256

from selectolax.parser import HTMLParser, Node


MDB_ID_PATTERN = re.compile(r"-(\d+)(?:$|[?#])")


@dataclass(frozen=True)
class Office:
    office_type: str
    label: str | None
    raw_address: str


@dataclass(frozen=True)
class ContactPoint:
    contact_type: str
    label: str
    url: str


@dataclass(frozen=True)
class Mandate:
    mandate_type: str
    constituency_number: int | None
    constituency_name: str | None
    constituency_url: str | None
    start_date: date | None


@dataclass(frozen=True)
class ExternalProfile:
    platform: str
    raw_label: str
    url: str


@dataclass(frozen=True)
class Affiliation:
    category: str
    organization_name: str
    organization_url: str | None
    role_name: str | None
    start_date: date | None
    end_date: date | None


@dataclass(frozen=True)
class MemberBiography:
    mdb_id: int
    first_name: str | None
    last_name: str
    name_prefix: str | None
    occupation: str | None
    parliamentary_group: str | None
    mandate_start: date | None
    offices: tuple[Office, ...]
    contact_points: tuple[ContactPoint, ...]
    mandates: tuple[Mandate, ...]
    external_profiles: tuple[ExternalProfile, ...]
    affiliations: tuple[Affiliation, ...]
    content_sha256: str


def parse_biography_page(html: str, source_url: str) -> MemberBiography:
    """Extract explicitly present profile data from a Bundestag biography page."""
    mdb_id = _extract_mdb_id(source_url)
    document = HTMLParser(html)
    person = _extract_json_ld_person(document)
    intro = document.css_first(".m-biography__intro")

    if person is None or intro is None:
        raise ValueError("The Bundestag biography page does not contain the expected profile data.")

    info = intro.css_first(".m-biography__introInfo")
    occupation = info.css_first("span").text(strip=True) if info and info.css_first("span") else None
    parliamentary_group = info.css_first("strong").text(strip=True) if info and info.css_first("strong") else None
    member_role = _find_bundestag_role(person.get("memberOf", []))

    first_name = _string_or_none(person.get("givenName"))
    last_name = _required_string(person.get("familyName"), "familyName")
    name_prefix = _name_prefix(document)
    mandate_start = _parse_date(member_role.get("startDate") if member_role else None)

    return MemberBiography(
        mdb_id=mdb_id,
        first_name=first_name,
        last_name=last_name,
        name_prefix=name_prefix,
        occupation=occupation,
        parliamentary_group=parliamentary_group,
        mandate_start=mandate_start,
        offices=tuple(_extract_offices(document)),
        contact_points=tuple(_extract_contact_points(document, source_url)),
        mandates=tuple(_extract_mandates(document, mandate_start)),
        external_profiles=tuple(_extract_external_profiles(document)),
        affiliations=tuple(_extract_affiliations(person.get("memberOf", []))),
        content_sha256=_profile_content_hash(
            first_name,
            last_name,
            name_prefix,
            occupation,
            parliamentary_group,
            mandate_start,
        ),
    )


def _extract_mdb_id(source_url: str) -> int:
    match = MDB_ID_PATTERN.search(source_url)
    if not match:
        raise ValueError("The biography URL does not end with a Bundestag MDB ID.")
    return int(match.group(1))


def _extract_json_ld_person(document: HTMLParser) -> dict[str, object] | None:
    for script in document.css('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.text())
        except json.JSONDecodeError:
            continue
        person = _find_person(payload)
        if person is not None:
            return person
    return None


def _find_person(value: object) -> dict[str, object] | None:
    if isinstance(value, dict):
        if value.get("@type") == "Person":
            return value
        for nested in value.values():
            person = _find_person(nested)
            if person is not None:
                return person
    if isinstance(value, list):
        for nested in value:
            person = _find_person(nested)
            if person is not None:
                return person
    return None


def _find_bundestag_role(roles: object) -> dict[str, object] | None:
    if not isinstance(roles, list):
        return None
    for role in roles:
        if isinstance(role, dict) and role.get("roleName") == "Mitglied des Bundestages":
            return role
    return None


def _extract_affiliations(roles: object) -> list[Affiliation]:
    if not isinstance(roles, list):
        return []
    affiliations: list[Affiliation] = []
    for role in roles:
        if not isinstance(role, dict) or role.get("@type") != "Role":
            continue
        organization = role.get("memberOf")
        if not isinstance(organization, dict):
            continue
        name = _string_or_none(organization.get("name"))
        if name is None:
            continue
        affiliations.append(Affiliation(
            category="bundestag_role",
            organization_name=name,
            organization_url=_string_or_none(organization.get("url")),
            role_name=_string_or_none(role.get("roleName")),
            start_date=_parse_date(role.get("startDate")),
            end_date=_parse_date(role.get("endDate")),
        ))
    return affiliations


def _extract_offices(document: HTMLParser) -> list[Office]:
    offices: list[Office] = []
    for section in document.css(".m-marginal__item"):
        heading = section.css_first(".m-marginal__itemTitle")
        content = section.css_first(".m-marginal__itemContent")
        if heading is None or content is None:
            continue
        title = heading.text(strip=True)
        office_type = {"Abgeordnetenbüro": "bundestag", "Wahlkreisbüro": "constituency"}.get(title)
        if office_type is None:
            continue
        for paragraph in content.css("p"):
            raw_address = paragraph.text(separator="\n", strip=True)
            if raw_address and "Kontakt" not in raw_address:
                offices.append(Office(office_type=office_type, label=None, raw_address=raw_address))
    return offices


def _extract_contact_points(document: HTMLParser, source_url: str) -> list[ContactPoint]:
    contacts: list[ContactPoint] = []
    for link in document.css('.m-marginal__itemContent a[href*="contactform?mdbId="]'):
        url = link.attributes["href"]
        if url.startswith("/"):
            url = "https://www.bundestag.de" + url
        contacts.append(ContactPoint(contact_type="bundestag_contact_form", label=link.attributes.get("title", "Kontakt"), url=url))
    return contacts


def _extract_mandates(document: HTMLParser, mandate_start: date | None) -> list[Mandate]:
    mandates: list[Mandate] = []
    for item in document.css(".m-biography__constituencyInfoItem"):
        title = item.css_first(".m-biography__constituencyInfoItemTitle")
        link = item.css_first("a[href*='wahlkreissuche?wknr=']")
        if title is None or link is None:
            continue
        mandate_type = title.text(strip=True)
        label = link.text(strip=True)
        number_match = re.search(r"Wahlkreis\s+(\d+)", label)
        url = link.attributes["href"]
        mandates.append(Mandate(
            mandate_type=mandate_type,
            constituency_number=int(number_match.group(1)) if number_match else None,
            constituency_name=label,
            constituency_url="https://www.bundestag.de" + url if url.startswith("/") else url,
            start_date=mandate_start,
        ))
    return mandates


def _extract_external_profiles(document: HTMLParser) -> list[ExternalProfile]:
    profiles: list[ExternalProfile] = []
    for section in document.css(".m-marginal__item"):
        heading = section.css_first(".m-marginal__itemTitle")
        if heading is None or heading.text(strip=True) != "Profile im Internet":
            continue
        for link in section.css(".m-marginal__itemContent a[href]"):
            label = link.attributes.get("title") or link.text(strip=True)
            url = link.attributes["href"]
            profiles.append(ExternalProfile(platform=label.lower(), raw_label=label, url=url))
    return profiles


def _name_prefix(document: HTMLParser) -> str | None:
    heading = document.css_first(".m-biography__introName")
    return heading.attributes.get("data-title") if heading else None


def _parse_date(value: object) -> date | None:
    return date.fromisoformat(value) if isinstance(value, str) else None


def _profile_content_hash(
    first_name: str | None,
    last_name: str,
    name_prefix: str | None,
    occupation: str | None,
    parliamentary_group: str | None,
    mandate_start: date | None,
) -> str:
    profile = {
        "first_name": first_name,
        "last_name": last_name,
        "name_prefix": name_prefix,
        "occupation": occupation,
        "parliamentary_group": parliamentary_group,
        "mandate_start": mandate_start.isoformat() if mandate_start else None,
    }
    return sha256(json.dumps(profile, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _required_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"The biography page is missing {field}.")
    return value


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) and value else None