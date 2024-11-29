from django.contrib.auth.models import Group

def create_default_groups(sender, **kwargs):
    """
    Crea los grupos predeterminados: clientes, vendedores, administradores.
    """
    groups = ['clientes', 'vendedores', 'administradores']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)