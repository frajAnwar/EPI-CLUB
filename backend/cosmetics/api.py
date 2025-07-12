from rest_framework import viewsets, status
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import ProfileBanner, UserBanner
from .serializers import ProfileBannerSerializer
from .filters import ProfileBannerFilter
from accounts.models import Currency, UserCurrency
from notifications.utils import send_user_notification

class ProfileBannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProfileBanner.objects.all().order_by('id')
    serializer_class = ProfileBannerSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    filterset_class = ProfileBannerFilter

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        banner = self.get_object()
        user = request.user

        if UserBanner.objects.filter(user=user, banner=banner).exists():
            return Response({'error': 'You already own this banner.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assume the first currency is the primary one for the shop
            primary_currency = Currency.objects.first()
            if not primary_currency:
                return Response({'error': 'Shop currency not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            user_currency, created = UserCurrency.objects.get_or_create(
                user=user, 
                currency=primary_currency
            )

            if user_currency.balance < banner.cost:
                return Response({'error': 'You do not have enough currency.'}, status=status.HTTP_400_BAD_REQUEST)

            user_currency.balance -= banner.cost
            user_currency.save()
            UserBanner.objects.create(user=user, banner=banner)

            # Send notification to user
            message = f"You purchased the banner '{banner.name}' for {banner.cost} {primary_currency.name}."
            send_user_notification(user, message)

            return Response({'status': 'Banner purchased successfully!'})

        except Currency.DoesNotExist:
            return Response({'error': 'Shop currency not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
