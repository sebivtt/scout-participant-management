# Karte der Schnittstellen

Welche Anfrage des Frontends welche Klasse im Backend trifft und welche Rechteprüfung dort gilt. Erzeugt von `backend/tools/schnittstellen_karte.py`, nicht von Hand bearbeiten. `tests/test_frontend_abgleich.py` prüft, dass die Karte zum Code passt.

`{x}` steht für eine Kennung, z. B. die Nummer einer Veranstaltung. „Rechte“ nennt die Rechteklassen der Backend-Klasse. Prüft eine Klasse weitere Rechte erst beim Speichern, steht das in `backend/tests/test_schreibrechte_inventar.py`. Nicht aufgeführt sind die abgeschalteten Module Essensplanung und Programmideen.


## auth

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| POST | `/auth/check-email/` | `authentication.views.CheckEmail` | AllowAny | `src/modules/auth/services/checking.ts:9` |
| POST | `/auth/check-password/` | `authentication.views.CheckPassword` | AllowAny | `src/modules/auth/services/checking.ts:12` |
| POST | `/auth/check-username/` | `authentication.views.CheckUsername` | AllowAny | `src/modules/auth/services/checking.ts:6` |
| GET | `/auth/groups/` | `authentication.views.GroupViewSet` | IsAuthenticated | `src/modules/auth/services/mapping.ts:18` |
| POST | `/auth/register/` | `authentication.views.RegisterViewSet` | AllowAny | `src/modules/auth/services/register.ts:6` |
| POST | `/basic/check-zip-code/` | `basic.views.CheckZipCodeViewSet` | AllowAny | `src/modules/auth/services/checking.ts:15` |
| GET | `/basic/eat-habits/` | `basic.views.EatHabitViewSet` | IsStaffOrReadOnly | `src/modules/auth/services/mapping.ts:27` |
| GET | `/basic/gender/` | `basic.views.GenderViewSet` | AllowAny | `src/modules/auth/services/mapping.ts:6` |
| GET | `/basic/scout-hierarchy-detail/` | `basic.views.ScoutHierarchyDetailedViewSet` | IsStaffOrReadOnly | `src/modules/auth/services/mapping.ts:9` |
| GET | `/basic/scout-orga-level/` | `basic.views.ScoutOrgaLevelViewSet` | IsStaffOrReadOnly | `src/modules/auth/services/mapping.ts:21` |
| GET | `/basic/theme/` | `basic.views.FrontendThemeViewSet` | IsAuthenticated, IsStaffOrReadOnly | `src/modules/auth/services/mapping.ts:12` |
| GET | `/event/attribute-choices/` | `anmelde_tool.attributes.views.AttributeTypeViewSet` | IsAuthenticated | `src/modules/auth/services/mapping.ts:24` |
| GET | `/event/choices/scout-level-types/` | `anmelde_tool.event.choices.views.ScoutLevelTypesViewSet` | AllowAny | `src/modules/auth/services/mapping.ts:15` |
| GET | `/event/email-sets/` | `anmelde_tool.email_services.views.StandardEmailViewSet` | IsAuthenticated, IsStaffOrReadOnly | `src/modules/auth/services/mapping.ts:30` |
| GET | `/event/event-location/` | `anmelde_tool.event.views.EventLocationViewSet` | IsAuthenticated | `src/modules/auth/services/mapping.ts:33` |
| POST | `/event/event/{x}/check-person/` | `anmelde_tool.registration.views.EventCheckPersonViewSet` | IsAuthenticated | `src/modules/auth/services/checking.ts:23` |
| POST | `/event/registration/{x}/check-person/` | `anmelde_tool.registration.views.CheckPersonViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/auth/services/checking.ts:18` |

## dashboard

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/auth/my-own-requests/` | `authentication.views.MyOwnRequestGroupAccessViewSet` | IsAuthenticated | `src/modules/dashboard/services/index.ts:15` |
| GET | `/auth/my-requests/` | `authentication.views.MyDecidableRequestGroupAccessViewSet` | IsAuthenticated | `src/modules/dashboard/services/index.ts:12` |
| GET | `/basic/search/` | `basic.views.SearchViewSet` | IsAuthenticated | `src/modules/dashboard/components/search/SearchModal.vue:224` |
| GET | `/keycloak/statistics/group-count/` | `keycloak_auth.keycloak_statistics.views.GroupCountViewSet` | IsAuthenticated | `src/modules/dashboard/services/index.ts:6` |
| GET | `/keycloak/statistics/user-count/` | `keycloak_auth.keycloak_statistics.views.UsersCountViewSet` | IsAuthenticated | `src/modules/dashboard/services/index.ts:9` |

## event

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/auth/groups/` | `authentication.views.GroupViewSet` | IsAuthenticated | `src/modules/event/services/mapping.ts:29` |
| GET | `/basic/eat-habits/` | `basic.views.EatHabitViewSet` | IsStaffOrReadOnly | `src/modules/event/services/mapping.ts:32` |
| GET | `/basic/gender/` | `basic.views.GenderViewSet` | AllowAny | `src/modules/event/services/mapping.ts:17` |
| GET | `/basic/scout-hierarchy-detail/` | `basic.views.ScoutHierarchyDetailedViewSet` | IsStaffOrReadOnly | `src/modules/event/services/event.ts:148`, `src/modules/event/services/mapping.ts:20` |
| GET | `/basic/scout-orga-level/` | `basic.views.ScoutOrgaLevelViewSet` | IsStaffOrReadOnly | `src/modules/event/services/mapping.ts:8` |
| GET | `/basic/theme/` | `basic.views.FrontendThemeViewSet` | IsAuthenticated, IsStaffOrReadOnly | `src/modules/event/services/mapping.ts:23` |
| GET | `/event/attribute-choices/` | `anmelde_tool.attributes.views.AttributeTypeViewSet` | IsAuthenticated | `src/modules/event/services/mapping.ts:14` |
| GET | `/event/attribute-module/` | `anmelde_tool.attributes.views.AttributeModuleViewSet` | IsAuthenticated | `src/modules/event/services/attribute-module.ts:7` |
| POST | `/event/attribute-module/` | `anmelde_tool.attributes.views.AttributeModuleViewSet` | IsAuthenticated | `src/modules/event/services/attribute-module.ts:15` |
| DELETE | `/event/attribute-module/{x}/` | `anmelde_tool.attributes.views.AttributeModuleViewSet` | IsAuthenticated | `src/modules/event/services/attribute-module.ts:21` |
| GET | `/event/attribute-module/{x}/` | `anmelde_tool.attributes.views.AttributeModuleViewSet` | IsAuthenticated | `src/modules/event/services/attribute-module.ts:12` |
| PATCH | `/event/attribute-module/{x}/` | `anmelde_tool.attributes.views.AttributeModuleViewSet` | IsAuthenticated | `src/modules/event/services/attribute-module.ts:18` |
| PUT | `/event/boolean-attribute/{x}/` | `anmelde_tool.attributes.views.BooleanAttributeViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:51` |
| GET | `/event/cash/income/` | `anmelde_tool.event.cash.views.CashIncomeViewSet` | IsCashResponsiblePerson | `src/modules/event/services/cash-income.ts:7` |
| POST | `/event/cash/income/` | `anmelde_tool.event.cash.views.CashIncomeViewSet` | IsCashResponsiblePerson | `src/modules/event/services/cash-income.ts:15` |
| DELETE | `/event/cash/income/{x}/` | `anmelde_tool.event.cash.views.CashIncomeViewSet` | IsCashResponsiblePerson | `src/modules/event/services/cash-income.ts:21` |
| GET | `/event/cash/income/{x}/` | `anmelde_tool.event.cash.views.CashIncomeViewSet` | IsCashResponsiblePerson | `src/modules/event/services/cash-income.ts:12` |
| PUT | `/event/cash/income/{x}/` | `anmelde_tool.event.cash.views.CashIncomeViewSet` | IsCashResponsiblePerson | `src/modules/event/services/cash-income.ts:18` |
| POST | `/event/cash/mail-reminder/` | `anmelde_tool.event.cash.views.MailReminderViewSet` | IsAuthenticated | `src/modules/event/services/event.ts:116` |
| POST | `/event/cash/mail-single-reminder/` | `anmelde_tool.event.cash.views.MailSingleReminderViewSet` | IsAuthenticated | `src/modules/event/services/event.ts:119` |
| GET | `/event/choices/file-extension/` | `anmelde_tool.event.choices.views.FileExtensionViewSet` | IsAuthenticated | `src/modules/event/services/event-files.ts:29` |
| GET | `/event/choices/file-generation-status/` | `anmelde_tool.event.choices.views.FileGenerationStatusViewSet` | IsAuthenticated | `src/modules/event/services/event-files.ts:25` |
| GET | `/event/choices/file-type/` | `anmelde_tool.event.choices.views.FileTypeViewSet` | IsAuthenticated | `src/modules/event/services/event-files.ts:21` |
| GET | `/event/choices/scout-level-types/` | `anmelde_tool.event.choices.views.ScoutLevelTypesViewSet` | AllowAny | `src/modules/event/services/mapping.ts:26` |
| PUT | `/event/date-time-attribute/{x}/` | `anmelde_tool.attributes.views.DateTimeAttributeViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:63` |
| GET | `/event/email-sets/` | `anmelde_tool.email_services.views.StandardEmailViewSet` | IsAuthenticated, IsStaffOrReadOnly | `src/modules/event/services/mapping.ts:35` |
| GET | `/event/event-location/` | `anmelde_tool.event.views.EventLocationViewSet` | IsAuthenticated | `src/modules/event/services/location.ts:7`, `src/modules/event/services/mapping.ts:38` |
| POST | `/event/event-location/` | `anmelde_tool.event.views.EventLocationViewSet` | IsAuthenticated | `src/modules/event/services/location.ts:15` |
| DELETE | `/event/event-location/{x}/` | `anmelde_tool.event.views.EventLocationViewSet` | IsAuthenticated | `src/modules/event/services/location.ts:21` |
| GET | `/event/event-location/{x}/` | `anmelde_tool.event.views.EventLocationViewSet` | IsAuthenticated | `src/modules/event/services/location.ts:12` |
| PUT | `/event/event-location/{x}/` | `anmelde_tool.event.views.EventLocationViewSet` | IsAuthenticated | `src/modules/event/services/location.ts:18` |
| GET | `/event/event-overview/` | `anmelde_tool.event.views.EventOverviewViewSet` | IsAuthenticated | `src/modules/event/services/event.ts:17` |
| GET | `/event/event-read/` | `anmelde_tool.event.views.EventReadViewSet` | IsAuthenticated | `src/modules/event/services/event.ts:7` |
| GET | `/event/event-read/{x}/` | `anmelde_tool.event.views.EventReadViewSet` | IsAuthenticated | `src/modules/event/services/event.ts:52` |
| PATCH | `/event/event-update-partial/{x}/` | `anmelde_tool.event.views.EventPartialUpdateViewSet` | IsEventSuperResponsiblePerson | `src/modules/event/services/event.ts:65` |
| POST | `/event/event/` | `anmelde_tool.event.views.EventViewSet` | IsEventSuperResponsiblePerson | `src/modules/event/services/event.ts:58` |
| DELETE | `/event/event/{x}/` | `anmelde_tool.event.views.EventViewSet` | IsEventSuperResponsiblePerson | `src/modules/event/services/event.ts:69` |
| GET | `/event/event/{x}/` | `anmelde_tool.event.views.EventViewSet` | IsEventSuperResponsiblePerson | `src/modules/event/services/event.ts:55` |
| PUT | `/event/event/{x}/` | `anmelde_tool.event.views.EventViewSet` | IsEventSuperResponsiblePerson | `src/modules/event/services/event.ts:62` |
| GET | `/event/event/{x}/available-modules/` | `anmelde_tool.event.views.AvailableEventModulesViewSet` | IsSubEventSuperResponsiblePerson | `src/modules/event/services/event.ts:48` |
| GET | `/event/event/{x}/booking-options/` | `anmelde_tool.event.views.BookingOptionViewSet` | IsSubEventResponsiblePersonOrReadOnly | `src/modules/event/services/event.ts:22` |
| POST | `/event/event/{x}/booking-options/` | `anmelde_tool.event.views.BookingOptionViewSet` | IsSubEventResponsiblePersonOrReadOnly | `src/modules/event/services/event.ts:28` |
| GET | `/event/event/{x}/booking-options/{x}/` | `anmelde_tool.event.views.BookingOptionViewSet` | IsSubEventResponsiblePersonOrReadOnly | `src/modules/event/services/event.ts:25` |
| PUT | `/event/event/{x}/booking-options/{x}/` | `anmelde_tool.event.views.BookingOptionViewSet` | IsSubEventResponsiblePersonOrReadOnly | `src/modules/event/services/event.ts:31` |
| POST | `/event/event/{x}/event-module/` | `anmelde_tool.event.views.EventModuleViewSet` | IsSubEventSuperResponsiblePerson | `src/modules/event/services/event.ts:35` |
| DELETE | `/event/event/{x}/event-module/{x}/` | `anmelde_tool.event.views.EventModuleViewSet` | IsSubEventSuperResponsiblePerson | `src/modules/event/services/event.ts:44` |
| PATCH | `/event/event/{x}/event-module/{x}/` | `anmelde_tool.event.views.EventModuleViewSet` | IsSubEventSuperResponsiblePerson | `src/modules/event/services/event.ts:41` |
| PUT | `/event/event/{x}/event-module/{x}/` | `anmelde_tool.event.views.EventModuleViewSet` | IsSubEventSuperResponsiblePerson | `src/modules/event/services/event.ts:38` |
| GET | `/event/event/{x}/files/generate/` | `anmelde_tool.event.file_generator.views.GenerateFilesViewSet` | IsSubEventResponsiblePerson | `src/modules/event/services/event-files.ts:17`, `src/modules/event/services/event.ts:136` |
| POST | `/event/event/{x}/files/generate/` | `anmelde_tool.event.file_generator.views.GenerateFilesViewSet` | IsSubEventResponsiblePerson | `src/modules/event/services/event-files.ts:13`, `src/modules/event/services/event.ts:130` |
| GET | `/event/event/{x}/summary/` | `anmelde_tool.event.summary.views.EventSummaryViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:72` |
| GET | `/event/event/{x}/summary/age-groups/` | `anmelde_tool.event.summary.views.EventAgeGroupsSummaryViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:92` |
| GET | `/event/event/{x}/summary/attributes/` | `anmelde_tool.event.summary.views.EventModuleSummaryViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:98` |
| GET | `/event/event/{x}/summary/cash-list/` | `anmelde_tool.event.summary.views.CashSummaryListViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:103` |
| GET | `/event/event/{x}/summary/cash/` | `anmelde_tool.event.summary.views.CashSummaryViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:108` |
| GET | `/event/event/{x}/summary/detailed/` | `anmelde_tool.event.summary.views.EventDetailedSummaryViewSet` | IsSubEventSuperResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:122` |
| GET | `/event/event/{x}/summary/emails/registration-responsible-persons/` | `anmelde_tool.event.summary.views.EmailRegistrationResponsiblePersonsViewSet` | IsSubEventResponsiblePerson | `src/modules/event/services/event-mail.ts:8` |
| GET | `/event/event/{x}/summary/event-location/` | `anmelde_tool.event.summary.views.EventLocationViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:140` |
| GET | `/event/event/{x}/summary/food/` | `anmelde_tool.event.summary.views.EventFoodSummaryViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:86` |
| GET | `/event/event/{x}/summary/kpi/booking-options/` | `anmelde_tool.event.summary.kpi.views.BookingOptionViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:83` |
| GET | `/event/event/{x}/summary/kpi/total-participants/` | `anmelde_tool.event.summary.kpi.views.TotalParticipantsViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:77` |
| GET | `/event/event/{x}/summary/kpi/total-registrations/` | `anmelde_tool.event.summary.kpi.views.TotalRegistrationsViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:80` |
| POST | `/event/event/{x}/summary/merge-registrations/` | `anmelde_tool.event.summary.views.MergeRegistrationsViewSet` | IsSubEventSuperResponsiblePerson | `src/modules/event/services/event.ts:133` |
| GET | `/event/event/{x}/summary/participant-locations/` | `anmelde_tool.event.summary.views.RegistrationLocationViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:144` |
| GET | `/event/event/{x}/summary/registration-by-date/` | `anmelde_tool.event.summary.kpi.views.RegistrationByDateViewSet` | IsSubEventResponsiblePerson oder IsLeaderPerson | `src/modules/event/services/event.ts:151` |
| GET | `/event/files/available-templates/` | `anmelde_tool.event.file_generator.views.FileTemplateViewSet` | IsAuthenticated | `src/modules/event/services/event-files.ts:7`, `src/modules/event/services/event.ts:127` |
| PUT | `/event/float-attribute/{x}/` | `anmelde_tool.attributes.views.FloatAttributeViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:60` |
| PUT | `/event/integer-attribute/{x}/` | `anmelde_tool.attributes.views.IntegerAttributeViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:66` |
| GET | `/event/my-invitations/` | `anmelde_tool.event.views.MyInvitationsViewSet` | IsAuthenticated | `src/modules/event/services/event.ts:12` |
| GET | `/event/my-registrations/` | `anmelde_tool.registration.views.MyRegistrationViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:7` |
| GET | `/event/registration-read/{x}/` | `anmelde_tool.registration.views.RegistrationReadViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:12` |
| POST | `/event/registration/` | `anmelde_tool.registration.views.RegistrationViewSet` | IsRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:15` |
| DELETE | `/event/registration/{x}/` | `anmelde_tool.registration.views.RegistrationViewSet` | IsRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:21` |
| PUT | `/event/registration/{x}/` | `anmelde_tool.registration.views.RegistrationViewSet` | IsRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:18` |
| POST | `/event/registration/{x}/boolean-attribute/` | `anmelde_tool.registration.views.RegistrationBooleanAttributeViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:33` |
| GET | `/event/registration/{x}/cash-detail/` | `anmelde_tool.event.summary.views.CashDetailViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/event.ts:111` |
| POST | `/event/registration/{x}/date-time-attribute/` | `anmelde_tool.registration.views.RegistrationDateTimeAttributeViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:45` |
| POST | `/event/registration/{x}/float-attribute/` | `anmelde_tool.registration.views.RegistrationFloatAttributeViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:42` |
| POST | `/event/registration/{x}/integer-attribute/` | `anmelde_tool.registration.views.RegistrationIntegerAttributeViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:48` |
| POST | `/event/registration/{x}/registration-rating/` | `anmelde_tool.registration.views.RegistrationRatingViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:72` |
| POST | `/event/registration/{x}/send-confirmation-mail/` | `anmelde_tool.registration.views.SendConfirmationMail` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:69` |
| POST | `/event/registration/{x}/single-participant/` | `anmelde_tool.registration.views.RegistrationSingleParticipantViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:24` |
| DELETE | `/event/registration/{x}/single-participant/{x}/` | `anmelde_tool.registration.views.RegistrationSingleParticipantViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:30` |
| PUT | `/event/registration/{x}/single-participant/{x}/` | `anmelde_tool.registration.views.RegistrationSingleParticipantViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:27` |
| POST | `/event/registration/{x}/string-attribute/` | `anmelde_tool.registration.views.RegistrationStringAttributeViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:36` |
| POST | `/event/registration/{x}/travel-attribute/` | `anmelde_tool.registration.views.RegistrationTravelAttributeViewSet` | IsSubRegistrationResponsiblePerson | `src/modules/event/services/registration.ts:39` |
| PUT | `/event/string-attribute/{x}/` | `anmelde_tool.attributes.views.StringAttributeViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:54` |
| PUT | `/event/travel-attribute/{x}/` | `anmelde_tool.attributes.views.TravelAttributeViewSet` | IsAuthenticated | `src/modules/event/services/registration.ts:57` |
| GET | `/event/travel-type-choices/` | `anmelde_tool.attributes.views.TravelTypeViewSet` | IsAuthenticated | `src/modules/event/services/mapping.ts:11` |

## group

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/auth/my-groups/` | `authentication.views.UserGroupViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:70` |
| GET | `/keycloak/create-group-choice/` | `keycloak_auth.views.CreateGroupChoicesViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:16` |
| GET | `/keycloak/group/` | `keycloak_auth.views.AllGroupsViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:8` |
| POST | `/keycloak/group/` | `keycloak_auth.views.AllGroupsViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:57` |
| DELETE | `/keycloak/group/{x}/` | `keycloak_auth.views.AllGroupsViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:64` |
| GET | `/keycloak/group/{x}/` | `keycloak_auth.views.AllGroupsViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:13` |
| PUT | `/keycloak/group/{x}/` | `keycloak_auth.views.AllGroupsViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:60` |
| GET | `/keycloak/group/{x}/group-admins/` | `keycloak_auth.views.GroupGroupAdminViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:79` |
| GET | `/keycloak/group/{x}/inevitable-members/` | `keycloak_auth.views.GroupInvitableMemberViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:40` |
| POST | `/keycloak/group/{x}/invite/` | `keycloak_auth.views.InviteMemberViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:19` |
| POST | `/keycloak/group/{x}/kick/` | `keycloak_auth.views.KickMemberViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:22` |
| GET | `/keycloak/group/{x}/kickable-members/` | `keycloak_auth.views.GroupKickableMemberViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:47` |
| POST | `/keycloak/group/{x}/leave/` | `keycloak_auth.views.LeaveGroupViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:25` |
| GET | `/keycloak/group/{x}/members/` | `keycloak_auth.views.GroupMembersViewSet` | IsAuthenticated, IsGroupViewerOrMember | `src/modules/group/services/group.ts:54` |
| GET | `/keycloak/group/{x}/requests/` | `keycloak_auth.views.RequestGroupAccessViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:28` |
| POST | `/keycloak/group/{x}/requests/` | `keycloak_auth.views.RequestGroupAccessViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:31` |
| POST | `/keycloak/group/{x}/requests/{x}/accept/` | `keycloak_auth.views.AcceptRequestGroupAccessViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:37` |
| POST | `/keycloak/group/{x}/requests/{x}/decline/` | `keycloak_auth.views.DeclineRequestGroupAccessViewSet` | IsAuthenticated, IsGroupAdmin | `src/modules/group/services/group.ts:34` |
| GET | `/keycloak/group/{x}/user-admins/` | `keycloak_auth.views.GroupUserAdminViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:76` |
| GET | `/keycloak/groups-short/` | `keycloak_auth.views.ShortGroupsViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:73` |
| GET | `/keycloak/statistics/user-count/` | `keycloak_auth.keycloak_statistics.views.UsersCountViewSet` | IsAuthenticated | `src/modules/group/services/group.ts:67` |

## landing

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/basic/faq/` | `basic.views.DescriptionViewSet` | IsStaffOrReadOnly | `src/modules/landing/service/faq.ts:7` |
| GET | `/basic/faq/{x}/` | `basic.views.DescriptionViewSet` | IsStaffOrReadOnly | `src/modules/landing/service/faq.ts:13` |
| GET | `/basic/privacy/` | `basic.views.DescriptionViewSet` | IsStaffOrReadOnly | `src/modules/landing/service/privacy.ts:7` |
| GET | `/basic/privacy/{x}/` | `basic.views.DescriptionViewSet` | IsStaffOrReadOnly | `src/modules/landing/service/privacy.ts:13` |

## message

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| POST | `/message/issue-init-create/` | `messaging.views.IssueInitCreateViewSet` | AllowAny | `src/modules/message/services/issue.ts:15` |
| GET | `/message/issue-read/` | `messaging.views.IssueReadViewSet` | IsAuthenticated | `src/modules/message/services/issue.ts:7` |
| GET | `/message/issue-read/{x}/` | `messaging.views.IssueReadViewSet` | IsAuthenticated | `src/modules/message/services/issue.ts:12` |
| GET | `/message/issue-type-read-short/` | `messaging.views.IssueTypeReadShortViewSet` | IsStaffOrReadOnly | `src/modules/message/services/issueType.ts:12` |
| GET | `/message/issue-type-read/` | `messaging.views.IssueTypeReadViewSet` | IsStaffOrReadOnly | `src/modules/message/services/issueType.ts:7` |
| GET | `/message/issue-type-read/{x}/` | `messaging.views.IssueTypeReadViewSet` | IsStaffOrReadOnly | `src/modules/message/services/issueType.ts:18` |
| POST | `/message/issue-type/` | `messaging.views.IssueTypeViewSet` | IsStaffOrReadOnly | `src/modules/message/services/issueType.ts:22` |
| DELETE | `/message/issue-type/{x}/` | `messaging.views.IssueTypeViewSet` | IsStaffOrReadOnly | `src/modules/message/services/issueType.ts:30` |
| PUT | `/message/issue-type/{x}/` | `messaging.views.IssueTypeViewSet` | IsStaffOrReadOnly | `src/modules/message/services/issueType.ts:26` |
| DELETE | `/message/issue/{x}/` | `messaging.views.IssueViewSet` | IsAuthenticated | `src/modules/message/services/issue.ts:21` |
| PUT | `/message/issue/{x}/` | `messaging.views.IssueViewSet` | IsAuthenticated | `src/modules/message/services/issue.ts:18` |
| GET | `/message/message-prio/` | `messaging.views.MessagePriorityChoiceViewSet` | AllowAny | `src/modules/message/services/messagePrio.ts:7` |
| GET | `/message/message-read/` | `messaging.views.MessageReadViewSet` | IsAuthenticated | `src/modules/message/services/message.ts:7` |
| GET | `/message/message-read/{x}/` | `messaging.views.MessageReadViewSet` | IsAuthenticated | `src/modules/message/services/message.ts:13` |
| GET | `/message/message-statuses/` | `messaging.views.MessageStatusChoiceViewSet` | AllowAny | `src/modules/message/services/messageStatuses.ts:7` |
| POST | `/message/message/` | `messaging.views.MessageViewSet` | IsAuthenticated | `src/modules/message/services/message.ts:17` |
| DELETE | `/message/message/{x}/` | `messaging.views.MessageViewSet` | IsAuthenticated | `src/modules/message/services/message.ts:25` |
| PUT | `/message/message/{x}/` | `messaging.views.MessageViewSet` | IsAuthenticated | `src/modules/message/services/message.ts:21` |

## notification

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/auth/notification/all/` | `authentication.custom_notifications.views.AllNotificationViewSet` | IsAuthenticated | `src/modules/notification/services/notification.ts:8` |
| GET | `/auth/notification/all/{x}/` | `authentication.custom_notifications.views.AllNotificationViewSet` | IsAuthenticated | `src/modules/notification/services/notification.ts:18` |
| GET | `/auth/notification/count/` | `authentication.custom_notifications.views.NotificationCountViewSet` | IsAuthenticated | `src/modules/notification/services/notification.ts:13` |
| POST | `/auth/notification/mark-as-read/` | `authentication.custom_notifications.views.MarkAsReadViewSet` | IsAuthenticated | `src/modules/notification/services/notification.ts:21` |
| POST | `/auth/notification/mark-as-unread/` | `authentication.custom_notifications.views.MarkAsUnreadViewSet` | IsAuthenticated | `src/modules/notification/services/notification.ts:24` |

## person

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/auth/my-members-addable/` | `authentication.views.AddablePersons` | IsAuthenticated | `src/modules/person/services/person.ts:16` |
| POST | `/auth/my-members-upload/` | `authentication.views.MyMembersUploadViewSet` | IsAuthenticated | `src/modules/person/services/person.ts:33` |
| GET | `/auth/my-members/` | `authentication.views.MyMembersViewSet` | IsAuthenticated | `src/modules/person/services/person.ts:7` |
| POST | `/auth/my-members/` | `authentication.views.MyMembersViewSet` | IsAuthenticated | `src/modules/person/services/person.ts:22` |
| DELETE | `/auth/my-members/{x}/` | `authentication.views.MyMembersViewSet` | IsAuthenticated | `src/modules/person/services/person.ts:30` |
| GET | `/auth/my-members/{x}/` | `authentication.views.MyMembersViewSet` | IsAuthenticated | `src/modules/person/services/person.ts:13` |
| PUT | `/auth/my-members/{x}/` | `authentication.views.MyMembersViewSet` | IsAuthenticated | `src/modules/person/services/person.ts:26` |
| GET | `/keycloak/members/` | `keycloak_auth.views.AllMembersViewSet` | IsAuthenticated | `src/modules/person/services/user.ts:7` |
| GET | `/keycloak/members/{x}/` | `keycloak_auth.views.AllMembersViewSet` | IsAuthenticated | `src/modules/person/services/user.ts:13` |

## settings

| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |
| --- | --- | --- | --- | --- |
| GET | `/auth/my-tribe-verified/` | `authentication.views.MyTribeVerifiedViewSet` | IsAuthenticated | `src/modules/settings/services/personal-data.ts:30` |
| GET | `/auth/personal-data/` | `authentication.views.PersonalData` | IsAuthenticated | `src/modules/settings/services/personal-data.ts:7` |
| PUT | `/auth/personal-data/` | `authentication.views.PersonalData` | IsAuthenticated | `src/modules/settings/services/personal-data.ts:22` |
