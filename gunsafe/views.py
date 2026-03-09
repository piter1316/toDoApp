from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Weapon, WeaponType, Caliber, Magazine, Accessory, AmmoSafe, Shooting, Cleaning
from django.db.models import Sum
from datetime import date


@login_required(login_url='/accounts/login')
def gunsafe_home(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_weapon':
            name = request.POST.get('name')
            type_id = request.POST.get('weapon_type')
            caliber_ids = request.POST.getlist('caliber')
            serial_no = request.POST.get('serial_no')
            action_type = request.POST.get('action_type')
            
            weapon = Weapon.objects.create(
                user=request.user,
                name=name,
                weapon_type_id=type_id if type_id else None,
                serial_no=serial_no,
                action=action_type,
                purchase_date=request.POST.get('purchase_date') or None
            )
            if caliber_ids:
                weapon.calibers.set(caliber_ids)

        elif action == 'edit_weapon':
            weapon_id = request.POST.get('weapon_id')
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            
            weapon.name = request.POST.get('name')
            type_id = request.POST.get('weapon_type')
            weapon.weapon_type_id = type_id if type_id else None
            caliber_ids = request.POST.getlist('caliber')
            weapon.calibers.set(caliber_ids)
            weapon.serial_no = request.POST.get('serial_no')
            weapon.action = request.POST.get('action_type')
            weapon.purchase_date = request.POST.get('purchase_date') or None
            weapon.is_sold = request.POST.get('is_sold') == 'on'
            weapon.save()

        elif action == 'add_shooting':
            weapon_id = request.POST.get('weapon_id')
            rounds = int(request.POST.get('rounds', 0))
            shooting_date = request.POST.get('date') or date.today()
            use_safe_ammo = request.POST.get('use_safe_ammo') == 'on'
            ammo_id = request.POST.get('ammo_id')
            ammo_safe = None
            
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            
            if use_safe_ammo and weapon.calibers.exists():
                # Odejmij od amunicji w szafie
                if ammo_id:
                    ammo_safe = AmmoSafe.objects.filter(id=ammo_id, user=request.user).first()
                else:
                    # Fallback do pierwszej dostępnej (jeśli id nie przekazano)
                    ammo_safe = AmmoSafe.objects.filter(user=request.user, caliber__in=weapon.calibers.all()).first()
                
                if ammo_safe:
                    ammo_safe.qty = max(0, ammo_safe.qty - rounds)
                    ammo_safe.save()

            ammo_info = ""
            if ammo_safe:
                parts = [
                    ammo_safe.caliber.name,
                    ammo_safe.manufacturer or "",
                    ammo_safe.typ or "",
                    f"{ammo_safe.grain}gr" if ammo_safe.grain else ""
                ]
                ammo_info = " ".join([p for p in parts if p]).strip()

            Shooting.objects.create(weapon=weapon, rounds=rounds, date=shooting_date, ammo_safe=ammo_safe, ammo_info=ammo_info)
            
            weapon.total_rounds_fired += rounds
            weapon.save()

        elif action == 'add_cleaning':
            weapon_id = request.POST.get('weapon_id')
            cleaning_date = request.POST.get('date') or date.today()
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            Cleaning.objects.create(weapon=weapon, date=cleaning_date)

        elif action == 'add_ammo':
            caliber_id = request.POST.get('caliber_id')
            manufacturer = request.POST.get('manufacturer')
            typ = request.POST.get('typ')
            grain = request.POST.get('grain')
            qty = int(request.POST.get('qty', 0))
            
            ammo, created = AmmoSafe.objects.get_or_create(
                user=request.user,
                caliber_id=caliber_id,
                manufacturer=manufacturer,
                typ=typ,
                grain=grain if grain else None,
                defaults={'qty': qty}
            )
            if not created:
                ammo.qty += qty
                ammo.save()

        elif action == 'ammo_correction':
            ammo_id = request.POST.get('ammo_id')
            qty = int(request.POST.get('qty', 0)) # ujemna wartość dla ubytku
            ammo = get_object_or_404(AmmoSafe, id=ammo_id, user=request.user)
            ammo.qty = max(0, ammo.qty + qty)
            ammo.save()

        elif action == 'delete_ammo':
            ammo_id = request.POST.get('ammo_id')
            ammo = get_object_or_404(AmmoSafe, id=ammo_id, user=request.user)
            ammo.delete()

        elif action == 'add_magazine':
            weapon_id = request.POST.get('weapon_id')
            capacity = int(request.POST.get('capacity', 0))
            manufacturer = request.POST.get('manufacturer')
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            Magazine.objects.create(weapon=weapon, capacity=capacity, manufacturer=manufacturer)

        elif action == 'add_accessory':
            weapon_id = request.POST.get('weapon_id')
            accessory_name = request.POST.get('accessory_name')
            description = request.POST.get('description')
            date_bought = request.POST.get('date_bought') or None
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            Accessory.objects.create(weapon=weapon, accessory_name=accessory_name, description=description, date_bought=date_bought)

        return redirect('gunsafe:gunsafe_home')

    weapons = Weapon.objects.filter(user=request.user, is_sold=False).select_related('weapon_type').prefetch_related('calibers', 'magazines', 'accessories', 'shootings', 'cleanings')
    
    for weapon in weapons:
        last_cleaning = weapon.last_cleaning
        if last_cleaning:
            rounds_since_cleaning = weapon.shootings.filter(date__gt=last_cleaning.date).aggregate(Sum('rounds'))['rounds__sum'] or 0
        else:
            rounds_since_cleaning = weapon.total_rounds_fired
        weapon.rounds_since_cleaning = rounds_since_cleaning

    ammo_inventory = AmmoSafe.objects.filter(user=request.user).select_related('caliber').order_by('caliber__name', 'manufacturer', 'typ', 'grain')
    weapon_types = WeaponType.objects.all().order_by('name')
    calibers = Caliber.objects.all().order_by('name')

    # Sumy po kalibrze
    ammo_by_caliber = AmmoSafe.objects.filter(user=request.user).values('caliber__name').annotate(total_qty=Sum('qty')).order_by('caliber__name')
    
    # Całkowita suma wszystkich pocisków
    total_ammo = ammo_inventory.aggregate(Sum('qty'))['qty__sum'] or 0

    context = {
        'weapons': weapons,
        'ammo_inventory': ammo_inventory,
        'weapon_types': weapon_types,
        'calibers': calibers,
        'ammo_by_caliber': ammo_by_caliber,
        'total_ammo': total_ammo,
        'today': date.today(),
    }
    return render(request, 'gunsafe/home.html', context)
    

@login_required(login_url='/accounts/login')
def gunsafe_archive(request):
    weapons = Weapon.objects.filter(user=request.user, is_sold=True).select_related('weapon_type').prefetch_related('calibers', 'magazines', 'accessories', 'shootings', 'cleanings')
    
    for weapon in weapons:
        last_cleaning = weapon.last_cleaning
        if last_cleaning:
            rounds_since_cleaning = weapon.shootings.filter(date__gt=last_cleaning.date).aggregate(Sum('rounds'))['rounds__sum'] or 0
        else:
            rounds_since_cleaning = weapon.total_rounds_fired
        weapon.rounds_since_cleaning = rounds_since_cleaning

    weapon_types = WeaponType.objects.all().order_by('name')
    calibers = Caliber.objects.all().order_by('name')

    context = {
        'weapons': weapons,
        'weapon_types': weapon_types,
        'calibers': calibers,
        'today': date.today(),
        'is_archive': True,
    }
    return render(request, 'gunsafe/archive.html', context)
    

@login_required(login_url='/accounts/login')
def weapon_details(request, weapon_id):
    weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit_weapon_details':
            weapon.name = request.POST.get('name')
            weapon.weapon_type_id = request.POST.get('weapon_type') or None
            caliber_ids = request.POST.getlist('caliber')
            weapon.calibers.set(caliber_ids)
            weapon.serial_no = request.POST.get('serial_no')
            weapon.action = request.POST.get('action_type')
            weapon.purchase_date = request.POST.get('purchase_date') or None
            weapon.is_sold = request.POST.get('is_sold') == 'on'
            weapon.save()

        elif action == 'edit_shooting':
            shooting_id = request.POST.get('shooting_id')
            shooting = get_object_or_404(Shooting, id=shooting_id, weapon=weapon)
            old_rounds = shooting.rounds
            old_ammo_safe = shooting.ammo_safe
            
            new_rounds = int(request.POST.get('rounds', 0))
            use_safe_ammo = request.POST.get('use_safe_ammo') == 'on'
            new_ammo_id = request.POST.get('ammo_id')
            
            # Koryguj stany amunicji
            # 1. Zwróć starą amunicję, jeśli była
            if old_ammo_safe:
                old_ammo_safe.qty += old_rounds
                old_ammo_safe.save()
            
            # 2. Pobierz nową amunicję, jeśli zaznaczono
            new_ammo_safe = None
            if use_safe_ammo and weapon.calibers.exists():
                if new_ammo_id:
                    new_ammo_safe = AmmoSafe.objects.filter(id=new_ammo_id, user=request.user).first()
                else:
                    new_ammo_safe = AmmoSafe.objects.filter(user=request.user, caliber__in=weapon.calibers.all()).first()
                
                if new_ammo_safe:
                    new_ammo_safe.qty = max(0, new_ammo_safe.qty - new_rounds)
                    new_ammo_safe.save()

            ammo_info = ""
            if new_ammo_safe:
                parts = [
                    new_ammo_safe.caliber.name,
                    new_ammo_safe.manufacturer or "",
                    new_ammo_safe.typ or "",
                    f"{new_ammo_safe.grain}gr" if new_ammo_safe.grain else ""
                ]
                ammo_info = " ".join([p for p in parts if p]).strip()
            elif old_ammo_safe and not use_safe_ammo:
                # Jeśli wcześniej była amunicja, a teraz nie chcemy zdejmować ze stanu,
                # to zachowujemy stary opis jeśli istniał, lub czyścimy?
                # User pewnie chce zachować info o tym co strzelał.
                ammo_info = shooting.ammo_info

            shooting.rounds = new_rounds
            shooting.date = request.POST.get('date') or date.today()
            shooting.ammo_safe = new_ammo_safe
            if ammo_info:
                shooting.ammo_info = ammo_info
            shooting.save()

            weapon.total_rounds_fired = weapon.total_rounds_fired - old_rounds + new_rounds
            weapon.save()

        elif action == 'delete_shooting':
            shooting_id = request.POST.get('shooting_id')
            shooting = get_object_or_404(Shooting, id=shooting_id, weapon=weapon)
            
            # Zwróć amunicję do szafy, jeśli była powiązana
            if shooting.ammo_safe:
                shooting.ammo_safe.qty += shooting.rounds
                shooting.ammo_safe.save()
            
            weapon.total_rounds_fired -= shooting.rounds
            weapon.save()
            shooting.delete()

        elif action == 'edit_cleaning':
            cleaning_id = request.POST.get('cleaning_id')
            cleaning = get_object_or_404(Cleaning, id=cleaning_id, weapon=weapon)
            cleaning.date = request.POST.get('date') or date.today()
            cleaning.save()

        elif action == 'delete_cleaning':
            cleaning_id = request.POST.get('cleaning_id')
            cleaning = get_object_or_404(Cleaning, id=cleaning_id, weapon=weapon)
            cleaning.delete()

        elif action == 'edit_accessory':
            acc_id = request.POST.get('accessory_id')
            acc = get_object_or_404(Accessory, id=acc_id, weapon=weapon)
            acc.accessory_name = request.POST.get('accessory_name')
            acc.description = request.POST.get('description')
            acc.date_bought = request.POST.get('date_bought') or None
            acc.save()

        elif action == 'delete_accessory':
            acc_id = request.POST.get('accessory_id')
            acc = get_object_or_404(Accessory, id=acc_id, weapon=weapon)
            acc.delete()

        elif action == 'edit_magazine':
            mag_id = request.POST.get('magazine_id')
            mag = get_object_or_404(Magazine, id=mag_id, weapon=weapon)
            mag.capacity = int(request.POST.get('capacity', 0))
            mag.manufacturer = request.POST.get('manufacturer')
            mag.save()

        elif action == 'delete_magazine':
            mag_id = request.POST.get('magazine_id')
            mag = get_object_or_404(Magazine, id=mag_id, weapon=weapon)
            mag.delete()

        elif action == 'add_shooting':
            rounds = int(request.POST.get('rounds', 0))
            shooting_date = request.POST.get('date') or date.today()
            use_safe_ammo = request.POST.get('use_safe_ammo') == 'on'
            ammo_id = request.POST.get('ammo_id')
            ammo_safe = None

            if use_safe_ammo and weapon.calibers.exists():
                if ammo_id:
                    ammo_safe = AmmoSafe.objects.filter(id=ammo_id, user=request.user).first()
                else:
                    ammo_safe = AmmoSafe.objects.filter(user=request.user, caliber__in=weapon.calibers.all()).first()
                
                if ammo_safe:
                    ammo_safe.qty = max(0, ammo_safe.qty - rounds)
                    ammo_safe.save()

            ammo_info = ""
            if ammo_safe:
                parts = [
                    ammo_safe.caliber.name,
                    ammo_safe.manufacturer or "",
                    ammo_safe.typ or "",
                    f"{ammo_safe.grain}gr" if ammo_safe.grain else ""
                ]
                ammo_info = " ".join([p for p in parts if p]).strip()

            Shooting.objects.create(weapon=weapon, rounds=rounds, date=shooting_date, ammo_safe=ammo_safe, ammo_info=ammo_info)
            weapon.total_rounds_fired += rounds
            weapon.save()

        elif action == 'add_cleaning':
            cleaning_date = request.POST.get('date') or date.today()
            Cleaning.objects.create(weapon=weapon, date=cleaning_date)

        elif action == 'add_magazine':
            capacity = int(request.POST.get('capacity', 0))
            manufacturer = request.POST.get('manufacturer')
            Magazine.objects.create(weapon=weapon, capacity=capacity, manufacturer=manufacturer)

        elif action == 'add_accessory':
            acc_name = request.POST.get('accessory_name')
            desc = request.POST.get('description')
            date_b = request.POST.get('date_bought') or None
            Accessory.objects.create(weapon=weapon, accessory_name=acc_name, description=desc, date_bought=date_b)

        elif action == 'delete_weapon':
            weapon.delete()
            return redirect('gunsafe:gunsafe_home')

        return redirect('gunsafe:weapon_details', weapon_id=weapon.id)

    shootings = weapon.shootings.select_related('ammo_safe').all().order_by('-date')
    cleanings = weapon.cleanings.all().order_by('-date')
    weapon_types = WeaponType.objects.all().order_by('name')
    calibers = Caliber.objects.all().order_by('name')

    last_cleaning = weapon.last_cleaning
    if last_cleaning:
        rounds_since_cleaning = weapon.shootings.filter(date__gt=last_cleaning.date).aggregate(Sum('rounds'))['rounds__sum'] or 0
    else:
        rounds_since_cleaning = weapon.total_rounds_fired
    weapon.rounds_since_cleaning = rounds_since_cleaning

    context = {
        'weapon': weapon,
        'shootings': shootings,
        'cleanings': cleanings,
        'weapon_types': weapon_types,
        'calibers': calibers,
        'ammo_inventory': AmmoSafe.objects.filter(user=request.user, caliber__in=weapon.calibers.all()).order_by('caliber__name', 'manufacturer', 'typ', 'grain'),
        'today': date.today(),
    }
    return render(request, 'gunsafe/weapon_details.html', context)
