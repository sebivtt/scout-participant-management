


# @receiver(post_save, sender=Registration, dispatch_uid='post_save_registration')
# def post_save_registration(sender: Registration, instance: Registration, created, raw, **kwargs):
#     if created:
#         services.send_registration_created_mail(instance_id=str(instance.id))
