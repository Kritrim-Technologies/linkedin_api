"""
Provides linkedin api-related code
"""
import random
import logging
from time import sleep, time
from urllib.parse import urlencode, quote_plus
import json
from operator import itemgetter
cookies_dir = '.cookie.jr'

def get_id_from_urn(urn):
    """
    Return the ID of a given Linkedin URN.
    Example: urn:li:fs_miniProfile:<id>
    """
    return urn.split(":")[3]

from api.client import Client


def default_evade():
    """
    A catch-all method to try and evade suspension from Linkedin.
    Currenly, just delays the request by a random (bounded) time
    """
    sleep(random.randint(2, 5))  # sleep a random duration to try and evade suspention


class Linkedin(object):
    """
    Class for accessing the LinkedIn API.
    :param username: Username of LinkedIn account.
    :type username: str
    :param password: Password of LinkedIn account.
    :type password: str
    """



    _MAX_SEARCH_COUNT = 49  # max seems to be 49, and min seems to be 2
    _MAX_REPEATED_REQUESTS = (
        200  # VERY conservative max requests count to avoid rate-limit
    )

    def __init__(
        self

    ):
        """Constructor method"""
        self.client = Client()
    

           
    def authenticate(self, username, password):
         return self.client.authenticate(username, password)

    def _fetch(self, uri, evade=default_evade, base_request=False, **kwargs):
        """GET request to Linkedin API"""
        evade()

        url = f"{self.client.API_BASE_URL if not base_request else self.client.LINKEDIN_BASE_URL}{uri}"
        print(url)
        return self.client.session.get(url, **kwargs)





    def search(self, params, limit=-1, offset=0):
        """Perform a LinkedIn search.
        :param params: Search parameters (see code)
        :type params: dict
        :param limit: Maximum length of the returned list, defaults to -1 (no limit)
        :type limit: int, optional
        :param offset: Index to start searching from
        :type offset: int, optional
        :return: List of search results
        :rtype: list
        """
        count = Linkedin._MAX_SEARCH_COUNT
        if limit is None:
            limit = -1

        results = []
        while True:
            # when we're close to the limit, only fetch what we need to
            if limit > -1 and limit - len(results) < count:
                count = limit - len(results)
            default_params = {
                "count": str(count),
                "filters": "List()",
                "origin": "GLOBAL_SEARCH_HEADER",
                "q": "all",
                "start": len(results) + offset,
                "queryContext": "List(spellCorrectionEnabled->true,relatedSearchesEnabled->true,kcardTypes->PROFILE|COMPANY)",
            }
            default_params.update(params)

            res = self._fetch(
                f"/search/blended?{urlencode(default_params, safe='(),')}",
                headers={"accept": "application/vnd.linkedin.normalized+json+2.1"},
            )
            data = res.json()

            new_elements = []
            elements = data.get("data", {}).get("elements", [])
            for i in range(len(elements)):
                new_elements.extend(elements[i]["elements"])
                # not entirely sure what extendedElements generally refers to - keyword search gives back a single job?
                # new_elements.extend(data["data"]["elements"][i]["extendedElements"])
            results.extend(new_elements)

            # break the loop if we're done searching
            # NOTE: we could also check for the `total` returned in the response.
            # This is in data["data"]["paging"]["total"]
            if (
                (-1 < limit <= len(results))  # if our results exceed set limit
                or len(results) / count >= Linkedin._MAX_REPEATED_REQUESTS
            ) or len(new_elements) == 0:
                break

        return results

    def search_people(
        self,
        connection_of=None,
        include_private_profiles=False,  # profiles without a public id, "Linkedin Member"
        **kwargs,
    ):
        
        
        filters = ["resultType->PEOPLE"]
        filters.append(f"connectionOf->{connection_of}")


        params = {"filters": "List({})".format(",".join(filters))}
        data = self.search(params, **kwargs)

        results = []
        for item in data:
            if not include_private_profiles and "publicIdentifier" not in item:
                continue
            results.append(
                {
                    "urn_id": get_id_from_urn(item.get("targetUrn")),
                    "distance": item.get("memberDistance", {}).get("value"),
                    "public_id": item.get("publicIdentifier"),
                    "tracking_id": get_id_from_urn(item.get("trackingUrn")),
                }
            )

        return results





    def get_profile_contact_info(self, public_id=None, urn_id=None):
        """Fetch contact information for a given LinkedIn profile. Pass a [public_id] or a [urn_id].
        :param public_id: LinkedIn public ID for a profile
        :type public_id: str, optional
        :param urn_id: LinkedIn URN ID for a profile
        :type urn_id: str, optional
        :return: Contact data
        :rtype: dict
        """
        res = self._fetch(
            f"/identity/profiles/{public_id or urn_id}/profileContactInfo"
        )
        data = res.json()

        contact_info = {
            "email_address": data.get("emailAddress"),
            "websites": [],
            "twitter": data.get("twitterHandles"),
            "birthdate": data.get("birthDateOn"),
            "ims": data.get("ims"),
            "phone_numbers": data.get("phoneNumbers", []),
        }

        websites = data.get("websites", [])
        for item in websites:
            if "com.linkedin.voyager.identity.profile.StandardWebsite" in item["type"]:
                item["label"] = item["type"][
                    "com.linkedin.voyager.identity.profile.StandardWebsite"
                ]["category"]
            elif "" in item["type"]:
                item["label"] = item["type"][
                    "com.linkedin.voyager.identity.profile.CustomWebsite"
                ]["label"]

            del item["type"]

        contact_info["websites"] = websites

        return contact_info

    def get_profile_skills(self, public_id=None, urn_id=None):
        """Fetch the skills listed on a given LinkedIn profile.
        :param public_id: LinkedIn public ID for a profile
        :type public_id: str, optional
        :param urn_id: LinkedIn URN ID for a profile
        :type urn_id: str, optional
        :return: List of skill objects
        :rtype: list
        """
        params = {"count": 100, "start": 0}
        res = self._fetch(
            f"/identity/profiles/{public_id or urn_id}/skills", params=params
        )
        data = res.json()

        data = data.get("elements", [])
        skills = []

        for item in data:
            skills.append(item['name'])
            

        return skills

    def get_profile(self, public_id=None, urn_id=None):
        """Fetch data for a given LinkedIn profile.
        :param public_id: LinkedIn public ID for a profile
        :type public_id: str, optional
        :param urn_id: LinkedIn URN ID for a profile
        :type urn_id: str, optional
        :return: Profile data
        :rtype: dict
        """
        # NOTE this still works for now, but will probably eventually have to be converted to
        # https://www.linkedin.com/voyager/api/identity/profiles/ACoAAAKT9JQBsH7LwKaE9Myay9WcX8OVGuDq9Uw
        res = self._fetch(f"/identity/profiles/{public_id or urn_id}/profileView")

        data = res.json()
        if data and "status" in data and data["status"] != 200:
            self.logger.info("request failed: {}".format(data["message"]))
            return {}

        # massage [profile] data
        profile = data["profile"]
        

        deleted_items = ["defaultLocale", "supportedLocales", "versionTag", "showEducationOnProfileTopCard", 'entityUrn', 'elt', 
        'geoCountryUrn', "geoLocation", "geoLocationBackfilled", "industryUrn", "member_urn", "profilePicture", "profilePictureOriginalImage", "miniProfile"]

        for item in deleted_items:
            if item in profile:
                del profile[item]

        # massage [experience] data
        experience = data["positionView"]["elements"]
        for item in experience:
            del_it = ["company", "companyUrn", "entityUrn", "geoUrn", "region"]
            for it in del_it:
                del item[it]


        profile["experience"] = experience

        # massage [education] data
        
        education = data["educationView"]["elements"]
        for item in education:
            del item['entityUrn']
            if 'school' in item:
                del item['school']
                del item['schoolUrn']

        profile["education"] = education

        # massage [languages] data
        languages = data["languageView"]["elements"]
        for item in languages:
            del item["entityUrn"]
        profile["languages"] = languages

        # massage [publications] data
        publications = data["publicationView"]["elements"]
        for item in publications:
            del item["entityUrn"]
            for author in item.get("authors", []):
                del author["entityUrn"]
        profile["publications"] = publications

        # massage [certifications] data
        certifications = data["certificationView"]["elements"]
        for item in certifications:
            del_it = ["entityUrn", "companyUrn", "company"]
            for it in del_it:
                del item[it]
        profile["certifications"] = certifications

        # massage [volunteer] data
        volunteer = data["volunteerExperienceView"]["elements"]
        for item in volunteer:
            del item["entityUrn"]
        profile["volunteer"] = volunteer

        # massage [honors] data
        honors = data["honorView"]["elements"]
        for item in honors:
            del item["entityUrn"]
        profile["honors"] = honors

        # massage [projects] data
        projects = data["projectView"]["elements"]
        for item in projects:
            del item["entityUrn"]
        profile["projects"] = projects

        return profile

    def get_profile_connections(self, urn_id):
        """Fetch first-degree connections for a given LinkedIn profile.
        :param urn_id: LinkedIn URN ID for a profile
        :type urn_id: str
        :return: List of search results
        :rtype: list
        """
        return self.search_people(connection_of=urn_id)


    def get_user_profile(self):
        """Get the current user profile. If not cached, a network request will be fired.
        :return: Profile data for currently logged in user
        :rtype: dict
        """
   
        res = self._fetch(f"/me")
        me_profile = res.json()
        return me_profile

