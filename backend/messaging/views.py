from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from keycloak_auth.access import member_group_ids
from keycloak_auth.permissions import IsStaffOrReadOnly
from messaging.models import Message, IssueType, Issue
from messaging.serializers import MessageSerializer, IssueReadSerializer, IssueTypeSerializer, IssueTypeReadSerializer, \
    IssueTypeReadShortSerializer, MessageReadSerializer, IssueSerializer
from basic.helper.choice_to_json import choice_to_json
from .choices import MessagePriorityChoise, MessageStatusChoise
from authentication.models import CustomUser


def visible_issues(request):
    """Anfragen, die die Person sehen darf: eigene, und solche, für deren Typ
    eine ihrer Gruppen zuständig ist. Staff sieht alle."""
    if request.user.is_staff:
        return Issue.objects.all().order_by('-created_at')
    return Issue.objects.filter(
        Q(created_by=request.user)
        | Q(issue_type__responsable_groups__keycloak_id__in=member_group_ids(request))
    ).distinct().order_by('-created_at')


# Issue
class IssueReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssueReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_queryset(self):
        return visible_issues(self.request)


class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssueSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Issue.objects.all().order_by('-created_at')
        else:
            return Issue.objects.filter(created_by=self.request.user).order_by('-created_at')


class IssueInitCreateViewSet(viewsets.ModelViewSet):
    """Kontaktformular: Anlegen geht auch ohne Login, alles andere nur für Staff."""
    queryset = Issue.objects.all()
    serializer_class = IssueReadSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        if request.user.id:
            request.data['created_by'] = CustomUser.objects.filter(id=request.user.id).first()
            request.data['created_by_name'] = None
            request.data['created_by_email'] = None
        else:
            request.data['created_by'] = None

        issue = Issue(
            created_by_name=request.data.get('created_by_name'),
            created_by_email=request.data.get('created_by_email'),
            created_by=request.data.get('created_by'),
            priority=request.data.get('priority'),
            issue_type_id=request.data.get('issue_type'),
            issue_subject=request.data.get('issue_subject'),
        )

        issue.save()

        message = Message(
            issue_id=issue.id,
            message_body=request.data.get('message_body'),
            created_by=request.data.get('created_by'),
        )
        message.save()

        return Response({'created issue and message'}, status=status.HTTP_201_CREATED)


# Message

class MessageReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageReadSerializer

    def get_queryset(self):
        return Message.objects.filter(issue__in=visible_issues(self.request)).order_by('-created_at')


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(issue__in=visible_issues(self.request)).order_by('-created_at')

    def create(self, request, *args, **kwargs) -> Response:
        # Nur zu Anfragen schreiben, die man sehen darf
        if not visible_issues(request).filter(id=request.data.get('issue')).exists():
            return Response('Keine Berechtigung für diese Anfrage.', status=status.HTTP_403_FORBIDDEN)
        request.data['created_by'] = request.user.id
        return super().create(request, *args, **kwargs)


# Issue-type

class IssueTypeReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeReadSerializer


class IssueTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeSerializer


class IssueTypeReadShortViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Auswahl im Kontaktformular
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeReadShortSerializer


# Prio

class MessagePriorityChoiceViewSet(viewsets.ViewSet):
    """
    Viewset for message priorities
    """
    permission_classes = [AllowAny]

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: standard django request
        @return: Response which MessagePriorityChoise choices
        """
        result = choice_to_json(MessagePriorityChoise.choices)
        return Response(result, status=status.HTTP_200_OK)


# Status

class MessageStatusChoiceViewSet(viewsets.ViewSet):
    """
    Viewset for message statues
    """
    permission_classes = [AllowAny]

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: standard django request
        @return: Response which MessageStatusChoise choices
        """
        result = choice_to_json(MessageStatusChoise.choices)
        return Response(result, status=status.HTTP_200_OK)
