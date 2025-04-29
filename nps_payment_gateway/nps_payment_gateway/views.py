from rest_framework import status, viewsets
from rest_framework.response import Response
from .models import NpsPayment
from .serializers import NpsPaymentSerializer

class NpsPaymentViewSet(viewsets.ModelViewSet):
    queryset = NpsPayment.objects.all()
    serializer_class = NpsPaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            self.perform_create(serializer)

            return Response({
                "message": "NPS payment created successfully.",
                "payment": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Failed to create NPS payment.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():

            self.perform_update(serializer)

            return Response({
                "message": "NPS payment updated successfully.",
                "payment": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Failed to update NPS payment.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

