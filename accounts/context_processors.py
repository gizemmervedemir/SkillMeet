from django.db.models import Q
from .models import MatchRequest, CustomUser

def chat_partners(request):
    if not request.user.is_authenticated:
        return {}

    # Kabul edilmiş eşleşmelerden karşı tarafları topla
    matches = MatchRequest.objects.filter(
        Q(sender=request.user, is_accepted=True) | Q(receiver=request.user, is_accepted=True)
    )

    partners = set()
    for match in matches:
        if match.sender == request.user:
            partners.add(match.receiver)
        else:
            partners.add(match.sender)

    return {'chat_partners': partners}