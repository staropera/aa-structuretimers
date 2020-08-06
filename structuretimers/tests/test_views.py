from datetime import timedelta
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import now

from allianceauth.tests.auth_utils import AuthUtils

from ..models import Timer
from .. import views
from . import LoadTestDataMixin, create_test_user


MODULE_PATH = "structures.views"


def get_json_response(response: object):
    return json.loads(response.content.decode("utf-8"))


@patch("structuretimers.models.TIMERBOARD2_NOTIFICATIONS_ENABLED", False)
class TestListData(LoadTestDataMixin, TestCase):
    @patch("structuretimers.models.TIMERBOARD2_NOTIFICATIONS_ENABLED", False)
    def setUp(self):
        self.factory = RequestFactory()

        # user
        self.user_1 = create_test_user(self.character_1)
        self.user_2 = create_test_user(self.character_2)
        self.user_3 = create_test_user(self.character_3)

        # timers
        self.timer_1 = Timer(
            structure_name="Timer 1",
            date=now() + timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            user=self.user_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        self.timer_1.save()
        self.timer_2 = Timer(
            structure_name="Timer 2",
            date=now() - timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            user=self.user_1,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
        )
        self.timer_2.save()
        self.timer_3 = Timer(
            structure_name="Timer 3",
            date=now() - timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            user=self.user_1,
            eve_solar_system=self.system_enaluri,
            structure_type=self.type_astrahus,
        )
        self.timer_3.save()

    def test_timer_list_view_loads(self):
        request = self.factory.get(reverse("structuretimers:timer_list"))
        request.user = self.user_1
        response = views.timer_list(request)
        self.assertEqual(response.status_code, 200)

    def _call_timer_list_data_and_get_timer_ids(
        self, tab_name: str = "current", user: User = None
    ) -> set:
        if not user:
            user = self.user_1
        request = self.factory.get(
            reverse("structuretimers:timer_list_data", args=[tab_name])
        )
        request.user = user
        response = views.timer_list_data(request, tab_name)
        self.assertEqual(response.status_code, 200)
        return {x["id"] for x in get_json_response(response)}

    def test_timer_list_data_current_and_past(self):
        # test current timers
        timer_ids = self._call_timer_list_data_and_get_timer_ids("current")
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

        # test past timers
        timer_ids = self._call_timer_list_data_and_get_timer_ids("past")
        expected = {self.timer_2.id, self.timer_3.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_corp_restricted_to_corp_member(self):
        timer_4 = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            user=self.user_2,
            visibility=Timer.VISIBILITY_CORPORATION,
        )
        timer_4.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_corp_restricted_to_non_corp_member(self):
        timer = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            visibility=Timer.VISIBILITY_CORPORATION,
        )
        timer.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_alliance_restricted_to_alliance_member(self):
        timer_4 = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            eve_alliance=self.alliance_1,
            user=self.user_2,
            visibility=Timer.VISIBILITY_ALLIANCE,
        )
        timer_4.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_alliance_restricted_to_non_alliance_member(self):
        timer = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            eve_alliance=self.alliance_3,
            user=self.user_3,
            visibility=Timer.VISIBILITY_ALLIANCE,
        )
        timer.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_show_opsec_restricted_to_opsec_member(self):
        AuthUtils.add_permission_to_user_by_name(
            "structuretimers.view_opsec_timer", self.user_1
        )
        timer_4 = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            is_opsec=True,
        )
        timer_4.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_opsec_restricted_to_non_opsec_member(self):
        timer = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            is_opsec=True,
        )
        timer.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_dont_show_opsec_corp_restricted_to_opsec_member_other_corp(self):
        AuthUtils.add_permission_to_user_by_name(
            "structuretimers.view_opsec_timer", self.user_1
        )
        timer = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            user=self.user_3,
            is_opsec=True,
            visibility=Timer.VISIBILITY_CORPORATION,
        )
        timer.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id}
        self.assertSetEqual(timer_ids, expected)

    def test_always_show_timers_created_by_user(self):
        timer_4 = Timer(
            structure_name="Timer 4",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=8),
            eve_character=self.character_3,
            eve_corporation=self.corporation_3,
            visibility=Timer.VISIBILITY_CORPORATION,
            user=self.user_1,
        )
        timer_4.save()
        timer_ids = self._call_timer_list_data_and_get_timer_ids()
        expected = {self.timer_1.id, timer_4.id}
        self.assertSetEqual(timer_ids, expected)


@patch("structuretimers.models.TIMERBOARD2_NOTIFICATIONS_ENABLED", False)
class TestGetTimerData(LoadTestDataMixin, TestCase):
    @patch("structuretimers.models.TIMERBOARD2_NOTIFICATIONS_ENABLED", False)
    def setUp(self):
        self.factory = RequestFactory()

        # user
        self.user_1 = create_test_user(self.character_1)

        # timers
        self.timer_1 = Timer(
            structure_name="Timer 1",
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            date=now() + timedelta(hours=4),
            eve_character=self.character_1,
            eve_corporation=self.corporation_1,
            user=self.user_1,
        )
        self.timer_1.save()

    def test_normal(self):
        request = self.factory.get(
            reverse("structuretimers:get_timer_data", args=[self.timer_1.pk])
        )
        request.user = self.user_1
        response = views.get_timer_data(request, self.timer_1.pk)
        self.assertEqual(response.status_code, 200)


class TestSelect2Views(LoadTestDataMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # user
        self.user_1 = create_test_user(self.character_1)

    def test_normal(self):
        request = self.factory.get(
            reverse("structuretimers:select2_solar_systems"), data={"term": "abu"}
        )
        request.user = self.user_1
        response = views.select2_solar_systems(request)
        self.assertEqual(response.status_code, 200)
        data = get_json_response(response)
        self.assertEqual(data, {"results": [{"id": 30004984, "text": "Abune"}]})