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
            caliber_id = request.POST.get('caliber')
            serial_no = request.POST.get('serial_no')
            action_type = request.POST.get('action_type')
            
            Weapon.objects.create(
                user=request.user,
                name=name,
                weapon_type_id=type_id if type_id else None,
                caliber_id=caliber_id if caliber_id else None,
                serial_no=serial_no,
                action=action_type
            )

        elif action == 'edit_weapon':
            weapon_id = request.POST.get('weapon_id')
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            
            weapon.name = request.POST.get('name')
            type_id = request.POST.get('weapon_type')
            weapon.weapon_type_id = type_id if type_id else None
            caliber_id = request.POST.get('caliber')
            weapon.caliber_id = caliber_id if caliber_id else None
            weapon.serial_no = request.POST.get('serial_no')
            weapon.action = request.POST.get('action_type')
            weapon.save()

        elif action == 'add_shooting':
            weapon_id = request.POST.get('weapon_id')
            rounds = int(request.POST.get('rounds', 0))
            shooting_date = request.POST.get('date') or date.today()
            use_safe_ammo = request.POST.get('use_safe_ammo') == 'on'
            
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            Shooting.objects.create(weapon=weapon, rounds=rounds, date=shooting_date)
            
            weapon.total_rounds_fired += rounds
            weapon.save()
            
            if use_safe_ammo and weapon.caliber:
                # Odejmij od amunicji w szafie (najpierw od dowolnej dostępnej tego kalibru)
                ammo = AmmoSafe.objects.filter(user=request.user, caliber=weapon.caliber).first()
                if ammo:
                    ammo.qty = max(0, ammo.qty - rounds)
                    ammo.save()

        elif action == 'add_cleaning':
            weapon_id = request.POST.get('weapon_id')
            cleaning_date = request.POST.get('date') or date.today()
            weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)
            Cleaning.objects.create(weapon=weapon, date=cleaning_date)

        elif action == 'add_ammo':
            caliber_id = request.POST.get('caliber_id')
            manufacturer = request.POST.get('manufacturer')
            qty = int(request.POST.get('qty', 0))
            
            ammo, created = AmmoSafe.objects.get_or_create(
                user=request.user,
                caliber_id=caliber_id,
                manufacturer=manufacturer,
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

    weapons = Weapon.objects.filter(user=request.user).select_related('weapon_type', 'caliber').prefetch_related('magazines', 'accessories', 'shootings', 'cleanings')
    ammo_inventory = AmmoSafe.objects.filter(user=request.user).select_related('caliber')
    weapon_types = WeaponType.objects.all()
    calibers = Caliber.objects.all()

    context = {
        'weapons': weapons,
        'ammo_inventory': ammo_inventory,
        'weapon_types': weapon_types,
        'calibers': calibers,
        'today': date.today(),
    }
    return render(request, 'gunsafe/home.html', context)
    

@login_required(login_url='/accounts/login')
def weapon_details(request, weapon_id):
    weapon = get_object_or_404(Weapon, id=weapon_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit_weapon_details':
            weapon.name = request.POST.get('name')
            weapon.weapon_type_id = request.POST.get('weapon_type') or None
            weapon.caliber_id = request.POST.get('caliber') or None
            weapon.serial_no = request.POST.get('serial_no')
            weapon.action = request.POST.get('action_type')
            weapon.save()

        elif action == 'edit_shooting':
            shooting_id = request.POST.get('shooting_id')
            shooting = get_object_or_404(Shooting, id=shooting_id, weapon=weapon)
            old_rounds = shooting.rounds
            new_rounds = int(request.POST.get('rounds', 0))
            shooting.rounds = new_rounds
            shooting.date = request.POST.get('date') or date.today()
            shooting.save()

            weapon.total_rounds_fired = weapon.total_rounds_fired - old_rounds + new_rounds
            weapon.save()

        elif action == 'delete_shooting':
            shooting_id = request.POST.get('shooting_id')
            shooting = get_object_or_404(Shooting, id=shooting_id, weapon=weapon)
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
            Shooting.objects.create(weapon=weapon, rounds=rounds, date=shooting_date)
            weapon.total_rounds_fired += rounds
            weapon.save()
            if use_safe_ammo and weapon.caliber:
                ammo = AmmoSafe.objects.filter(user=request.user, caliber=weapon.caliber).first()
                if ammo:
                    ammo.qty = max(0, ammo.qty - rounds)
                    ammo.save()

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

    shootings = weapon.shootings.all().order_by('-date')
    cleanings = weapon.cleanings.all().order_by('-date')
    weapon_types = WeaponType.objects.all()
    calibers = Caliber.objects.all()

    context = {
        'weapon': weapon,
        'shootings': shootings,
        'cleanings': cleanings,
        'weapon_types': weapon_types,
        'calibers': calibers,
        'today': date.today(),
    }
    return render(request, 'gunsafe/weapon_details.html', context)
