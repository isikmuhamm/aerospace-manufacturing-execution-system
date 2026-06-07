# aircraft_production_app/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from aircraft_production_app.models import (
    Team, Personnel, PartType, AircraftModel, WorkOrder, Part, Aircraft,
    DefinedTeamTypes, PartCategory, AircraftModelChoices,
    PartStatusChoices, AircraftStatusChoices, WorkOrderStatusChoices
)

User = get_user_model()

# ==========================================
# 1. MODEL & VALIDATION TESTS
# ==========================================
class ModelTests(TestCase):
    def setUp(self):
        self.wing_team = Team.objects.create(name="Wing Team", team_type=DefinedTeamTypes.WING_TEAM)
        self.assembly_team = Team.objects.create(name="Assembly Team", team_type=DefinedTeamTypes.ASSEMBLY_TEAM)
        
        self.user_fabricator = User.objects.create_user(username="fabricator", password="password123")
        self.user_assembler = User.objects.create_user(username="assembler", password="password123")
        
        self.personnel_fabricator = Personnel.objects.create(user=self.user_fabricator, team=self.wing_team)
        self.personnel_assembler = Personnel.objects.create(user=self.user_assembler, team=self.assembly_team)
        
        self.part_type_wing, _ = PartType.objects.get_or_create(category=PartCategory.WING)
        self.part_type_fuselage, _ = PartType.objects.get_or_create(category=PartCategory.FUSELAGE)
        self.part_type_tail, _ = PartType.objects.get_or_create(category=PartCategory.TAIL)
        self.part_type_avionics, _ = PartType.objects.get_or_create(category=PartCategory.AVIONICS)
        
        self.model_tb2, _ = AircraftModel.objects.get_or_create(name=AircraftModelChoices.TB2)
        self.model_akinci, _ = AircraftModel.objects.get_or_create(name=AircraftModelChoices.AKINCI)

    def test_team_producible_category(self):
        self.assertEqual(self.wing_team.get_producible_part_category(), PartCategory.WING)
        self.assertTrue(self.assembly_team.can_perform_assembly())
        self.assertEqual(self.assembly_team.get_producible_part_category(), None)

    def test_part_creation_validations(self):
        # 1. Correct category and team validation (Wing team WING parts)
        part = Part(
            part_type=self.part_type_wing,
            aircraft_model_compatibility=self.model_tb2,
            produced_by_team=self.wing_team,
            created_by_personnel=self.personnel_fabricator
        )
        part.full_clean()
        part.save()
        self.assertTrue(part.serial_number.startswith("TB2-KNT-"))

        # 2. Invalid category (Wing team WING_TEAM trying to produce FUSELAGE parts)
        part_invalid = Part(
            part_type=self.part_type_fuselage,
            aircraft_model_compatibility=self.model_tb2,
            produced_by_team=self.wing_team,
            created_by_personnel=self.personnel_fabricator
        )
        with self.assertRaises(ValidationError):
            part_invalid.full_clean()

        # 3. Empty team (Team with no members trying to produce)
        empty_team = Team.objects.create(name="Empty Team", team_type=DefinedTeamTypes.FUSELAGE_TEAM)
        part_empty_team = Part(
            part_type=self.part_type_fuselage,
            aircraft_model_compatibility=self.model_tb2,
            produced_by_team=empty_team
        )
        with self.assertRaises(ValidationError):
            part_empty_team.full_clean()

    def test_part_soft_delete(self):
        part = Part.objects.create(
            part_type=self.part_type_wing,
            aircraft_model_compatibility=self.model_tb2,
            produced_by_team=self.wing_team,
            created_by_personnel=self.personnel_fabricator,
            status=PartStatusChoices.AVAILABLE
        )
        part.delete()
        self.assertEqual(part.status, PartStatusChoices.RECYCLED)

        # Cannot soft delete a part in status USED
        part_used = Part.objects.create(
            part_type=self.part_type_wing,
            aircraft_model_compatibility=self.model_tb2,
            produced_by_team=self.wing_team,
            created_by_personnel=self.personnel_fabricator,
            status=PartStatusChoices.USED
        )
        with self.assertRaises(ValidationError):
            part_used.delete()

    def test_work_order_validation_and_cancellation(self):
        # 1. Invalid assigned team (must be Assembly Team)
        wo_invalid = WorkOrder(
            aircraft_model=self.model_tb2,
            quantity=5,
            assigned_to_assembly_team=self.wing_team
        )
        with self.assertRaises(ValidationError):
            wo_invalid.full_clean()

        # 2. Save logic (new work order assigned automatically goes to ASSIGNED)
        wo = WorkOrder.objects.create(
            aircraft_model=self.model_tb2,
            quantity=2,
            assigned_to_assembly_team=self.assembly_team
        )
        self.assertEqual(wo.status, WorkOrderStatusChoices.ASSIGNED)

        # 3. WorkOrder soft-delete / cancellation behavior
        wing_part = Part.objects.create(part_type=self.part_type_wing, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.wing_team, created_by_personnel=self.personnel_fabricator)
        
        fuselage_team = Team.objects.create(name="Fuselage Team", team_type=DefinedTeamTypes.FUSELAGE_TEAM)
        p2 = Personnel.objects.create(user=User.objects.create_user(username="f2", password="password"), team=fuselage_team)
        fuse_part = Part.objects.create(part_type=self.part_type_fuselage, aircraft_model_compatibility=self.model_tb2, produced_by_team=fuselage_team, created_by_personnel=p2)
        
        tail_team = Team.objects.create(name="Tail Team", team_type=DefinedTeamTypes.TAIL_TEAM)
        p3 = Personnel.objects.create(user=User.objects.create_user(username="f3", password="password"), team=tail_team)
        tail_part = Part.objects.create(part_type=self.part_type_tail, aircraft_model_compatibility=self.model_tb2, produced_by_team=tail_team, created_by_personnel=p3)
        
        avionics_team = Team.objects.create(name="Avionics Team", team_type=DefinedTeamTypes.AVIONICS_TEAM)
        p4 = Personnel.objects.create(user=User.objects.create_user(username="f4", password="password"), team=avionics_team)
        avionics_part = Part.objects.create(part_type=self.part_type_avionics, aircraft_model_compatibility=self.model_tb2, produced_by_team=avionics_team, created_by_personnel=p4)
        
        aircraft = Aircraft.objects.create(
            aircraft_model=self.model_tb2,
            assembled_by_team=self.assembly_team,
            assembled_by_personnel=self.personnel_assembler,
            work_order=wo,
            wing=wing_part,
            fuselage=fuse_part,
            tail=tail_part,
            avionics=avionics_part,
            status=AircraftStatusChoices.ACTIVE
        )

        # Attempt to cancel/delete a work order that has active aircraft (should fail)
        with self.assertRaises(ValidationError):
            wo.delete()

    def test_aircraft_compatibility_validations(self):
        # 1. Invalid part compatibility (TB2 aircraft with AKINCI wing part)
        wing_akinci = Part.objects.create(
            part_type=self.part_type_wing,
            aircraft_model_compatibility=self.model_akinci,
            produced_by_team=self.wing_team,
            created_by_personnel=self.personnel_fabricator
        )
        
        aircraft = Aircraft(
            aircraft_model=self.model_tb2,
            assembled_by_team=self.assembly_team,
            assembled_by_personnel=self.personnel_assembler,
            wing=wing_akinci
        )
        with self.assertRaises(ValidationError):
            aircraft.full_clean()

        # 2. Active status requires all components
        aircraft_incomplete = Aircraft(
            aircraft_model=self.model_tb2,
            assembled_by_team=self.assembly_team,
            assembled_by_personnel=self.personnel_assembler,
            status=AircraftStatusChoices.ACTIVE
        )
        with self.assertRaises(ValidationError):
            aircraft_incomplete.full_clean()


# ==========================================
# 2. API VIEW TESTS
# ==========================================
class APIViewTests(APITestCase):
    def setUp(self):
        self.wing_team = Team.objects.create(name="Wing Team", team_type=DefinedTeamTypes.WING_TEAM)
        self.fuselage_team = Team.objects.create(name="Fuselage Team", team_type=DefinedTeamTypes.FUSELAGE_TEAM)
        self.tail_team = Team.objects.create(name="Tail Team", team_type=DefinedTeamTypes.TAIL_TEAM)
        self.avionics_team = Team.objects.create(name="Avionics Team", team_type=DefinedTeamTypes.AVIONICS_TEAM)
        self.assembly_team = Team.objects.create(name="Assembly Team", team_type=DefinedTeamTypes.ASSEMBLY_TEAM)
        
        self.user_admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpassword")
        self.user_fabricator = User.objects.create_user(username="fabricator", email="fabricator@example.com", password="password123")
        self.user_assembler = User.objects.create_user(username="assembler", email="assembler@example.com", password="password123")
        
        self.personnel_fabricator = Personnel.objects.create(user=self.user_fabricator, team=self.wing_team)
        self.personnel_assembler = Personnel.objects.create(user=self.user_assembler, team=self.assembly_team)
        
        self.part_type_wing, _ = PartType.objects.get_or_create(category=PartCategory.WING)
        self.part_type_fuselage, _ = PartType.objects.get_or_create(category=PartCategory.FUSELAGE)
        self.part_type_tail, _ = PartType.objects.get_or_create(category=PartCategory.TAIL)
        self.part_type_avionics, _ = PartType.objects.get_or_create(category=PartCategory.AVIONICS)
        
        self.model_tb2, _ = AircraftModel.objects.get_or_create(name=AircraftModelChoices.TB2)
        self.model_akinci, _ = AircraftModel.objects.get_or_create(name=AircraftModelChoices.AKINCI)
        
    def test_user_registration(self):
        url = reverse('api:api_user_register')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "password2": "securepassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_current_user_info(self):
        self.client.force_authenticate(user=self.user_fabricator)
        url = reverse('api:current-user-api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'fabricator')

    def test_part_creation_by_team(self):
        self.client.force_authenticate(user=self.user_fabricator)
        
        url = reverse('api:part-list')
        data = {
            "aircraft_model_compatibility": self.model_tb2.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['part_type_display'], 'Kanat')

    def test_invalid_aircraft_update_fails_api(self):
        # We need to authenticate as a user with update permissions on Aircraft (e.g. assembly team member or admin)
        self.client.force_authenticate(user=self.user_assembler)
        
        # Create valid TB2 parts
        wing = Part.objects.create(part_type=self.part_type_wing, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.wing_team, created_by_personnel=self.personnel_fabricator)
        
        # Create fuselage, tail, avionics teams and parts
        fuse_team = Team.objects.create(name="Fuse Team Test", team_type=DefinedTeamTypes.FUSELAGE_TEAM)
        fuse = Part.objects.create(part_type=self.part_type_fuselage, aircraft_model_compatibility=self.model_tb2, produced_by_team=fuse_team)
        
        tail_team = Team.objects.create(name="Tail Team Test", team_type=DefinedTeamTypes.TAIL_TEAM)
        tail = Part.objects.create(part_type=self.part_type_tail, aircraft_model_compatibility=self.model_tb2, produced_by_team=tail_team)
        
        avionics_team = Team.objects.create(name="Avionics Team Test", team_type=DefinedTeamTypes.AVIONICS_TEAM)
        avionics = Part.objects.create(part_type=self.part_type_avionics, aircraft_model_compatibility=self.model_tb2, produced_by_team=avionics_team)

        # Create TB2 aircraft
        aircraft = Aircraft.objects.create(
            aircraft_model=self.model_tb2,
            assembled_by_team=self.assembly_team,
            assembled_by_personnel=self.personnel_assembler,
            wing=wing,
            fuselage=fuse,
            tail=tail,
            avionics=avionics,
            status=AircraftStatusChoices.ACTIVE
        )
        
        # Try to change aircraft model to AKINCI via API (should fail because TB2 parts are attached)
        url = reverse('api:aircraft-detail', kwargs={'pk': aircraft.id})
        data = {
            "aircraft_model": self.model_akinci.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_aircraft_assembly_api(self):
        self.client.force_authenticate(user=self.user_assembler)
        url = reverse('api:assemble-aircraft-api')
        data = {
            "aircraft_model_id": self.model_tb2.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("missing_parts", response.data)

        # Add required parts to satisfy FIFO assembly
        Personnel.objects.create(user=User.objects.create_user(username="f2", password="password"), team=self.fuselage_team)
        Personnel.objects.create(user=User.objects.create_user(username="f3", password="password"), team=self.tail_team)
        Personnel.objects.create(user=User.objects.create_user(username="f4", password="password"), team=self.avionics_team)

        Part.objects.create(part_type=self.part_type_wing, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.wing_team, created_by_personnel=self.personnel_fabricator)
        Part.objects.create(part_type=self.part_type_fuselage, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.fuselage_team)
        Part.objects.create(part_type=self.part_type_tail, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.tail_team)
        Part.objects.create(part_type=self.part_type_avionics, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.avionics_team)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], AircraftStatusChoices.ACTIVE)

    def test_stock_levels_api(self):
        self.client.force_authenticate(user=self.user_admin)
        url = reverse('api:stock-levels-api')
        
        response = self.client.get(url, {'stock_type': 'parts'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        
        response = self.client.get(url, {'stock_type': 'aircrafts'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)


# ==========================================
# 3. SIGNAL TESTS
# ==========================================
class SignalTests(TestCase):
    def setUp(self):
        self.wing_team = Team.objects.create(name="Wing Team", team_type=DefinedTeamTypes.WING_TEAM)
        self.fuselage_team = Team.objects.create(name="Fuselage Team", team_type=DefinedTeamTypes.FUSELAGE_TEAM)
        self.tail_team = Team.objects.create(name="Tail Team", team_type=DefinedTeamTypes.TAIL_TEAM)
        self.avionics_team = Team.objects.create(name="Avionics Team", team_type=DefinedTeamTypes.AVIONICS_TEAM)
        self.assembly_team = Team.objects.create(name="Assembly Team", team_type=DefinedTeamTypes.ASSEMBLY_TEAM)
        
        self.user_fabricator = User.objects.create_user(username="fabricator", password="password123")
        self.user_assembler = User.objects.create_user(username="assembler", password="password123")
        
        self.personnel_fabricator = Personnel.objects.create(user=self.user_fabricator, team=self.wing_team)
        self.personnel_assembler = Personnel.objects.create(user=self.user_assembler, team=self.assembly_team)
        
        self.part_type_wing, _ = PartType.objects.get_or_create(category=PartCategory.WING)
        self.part_type_fuselage, _ = PartType.objects.get_or_create(category=PartCategory.FUSELAGE)
        self.part_type_tail, _ = PartType.objects.get_or_create(category=PartCategory.TAIL)
        self.part_type_avionics, _ = PartType.objects.get_or_create(category=PartCategory.AVIONICS)
        
        self.model_tb2, _ = AircraftModel.objects.get_or_create(name=AircraftModelChoices.TB2)
        
        Personnel.objects.create(user=User.objects.create_user(username="f2", password="password"), team=self.fuselage_team)
        Personnel.objects.create(user=User.objects.create_user(username="f3", password="password"), team=self.tail_team)
        Personnel.objects.create(user=User.objects.create_user(username="f4", password="password"), team=self.avionics_team)

        self.wo = WorkOrder.objects.create(
            aircraft_model=self.model_tb2,
            quantity=2,
            assigned_to_assembly_team=self.assembly_team
        )

    def _create_parts_and_assemble(self):
        wing_part = Part.objects.create(part_type=self.part_type_wing, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.wing_team, created_by_personnel=self.personnel_fabricator)
        fuse_part = Part.objects.create(part_type=self.part_type_fuselage, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.fuselage_team)
        tail_part = Part.objects.create(part_type=self.part_type_tail, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.tail_team)
        avionics_part = Part.objects.create(part_type=self.part_type_avionics, aircraft_model_compatibility=self.model_tb2, produced_by_team=self.avionics_team)
        
        return Aircraft.objects.create(
            aircraft_model=self.model_tb2,
            assembled_by_team=self.assembly_team,
            assembled_by_personnel=self.personnel_assembler,
            work_order=self.wo,
            wing=wing_part,
            fuselage=fuse_part,
            tail=tail_part,
            avionics=avionics_part,
            status=AircraftStatusChoices.ACTIVE
        )

    def test_work_order_status_sync(self):
        self.assertEqual(self.wo.status, WorkOrderStatusChoices.ASSIGNED)
        
        # 1. Assemble first aircraft -> status should change to IN_PROGRESS
        ac1 = self._create_parts_and_assemble()
        self.wo.refresh_from_db()
        self.assertEqual(self.wo.status, WorkOrderStatusChoices.IN_PROGRESS)

        # 2. Assemble second aircraft -> status should change to COMPLETED
        ac2 = self._create_parts_and_assemble()
        self.wo.refresh_from_db()
        self.assertEqual(self.wo.status, WorkOrderStatusChoices.COMPLETED)

        # 3. Soft-delete (recycle) one aircraft -> status should revert to IN_PROGRESS (since active count is 1)
        ac2.delete()
        self.wo.refresh_from_db()
        self.assertEqual(self.wo.status, WorkOrderStatusChoices.IN_PROGRESS)

    def test_parts_made_available_on_aircraft_deletion(self):
        ac = self._create_parts_and_assemble()
        wing_part = ac.wing
        
        wing_part.refresh_from_db()
        self.assertEqual(wing_part.status, PartStatusChoices.USED)

        ac.delete()
        
        wing_part.refresh_from_db()
        self.assertEqual(wing_part.status, PartStatusChoices.AVAILABLE)
