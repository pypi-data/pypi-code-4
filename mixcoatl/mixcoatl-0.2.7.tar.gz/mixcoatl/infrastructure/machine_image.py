from mixcoatl.resource import Resource
from mixcoatl.decorators.lazy import lazy_property

# TODO: certain images cause weird redirect
# m = MachineImage(284555) redirect loop
# m = MachineImage(284831) no loop
class MachineImage(Resource):
    PATH = 'infrastructure/MachineImage'
    COLLECTION_NAME = 'images'
    PRIMARY_KEY = 'machine_image_id'

    def __init__(self, machine_image_id = None, *args, **kwargs):
        """A machine image is the baseline image or template from which
            virtual machines may be provisioned.
        """
        Resource.__init__(self, request_details='basic')
        self.__machine_image_id = machine_image_id

    @property
    def machine_image_id(self):
        """`int` - The unique enStratus id for this machine image"""
        return self.__machine_image_id

    @lazy_property
    def architecture(self):
        """`str` - The underlying CPU architecture of the virtual machine in question"""
        return self.__architecture

    @lazy_property
    def cloud(self):
        """`dict` - The cloud in which this machine image is installed"""
        return self.__cloud

    @lazy_property
    def creation_timestamp(self):
        """`str` - The date and time this machine image was first created

        .. .note::

                Some clouds do not report his value and it may therefore be `00:00 UTC January 1, 1970

        """
        return self.__creation_timestamp

    @lazy_property
    def customer(self):
        """`dict` - The customer in whose library this machine image record is being managed"""
        return self.__customer

    @lazy_property
    def budget(self):
        """`int` - The id of the billing code against which costs associated are
            billed for this machine image
        """
        return self.__budget

    @lazy_property
    def description(self):
        """`str` - The description of the machine image established in enStratus"""
        return self.__description

    @lazy_property
    def name(self):
        """`str` - The user friendly name for the machine image"""
        return self.__name

    @lazy_property
    def owning_account(self):
        """`dict` - The enStratus cloud account that is the account under which
            the machine image is registered

            .. .note::

                This value may be empty if the machine image belongs to an account
                not using enStratus

        """
        return self.__owning_account

    @lazy_property
    def owning_cloud_account_number(self):
        """`str` - The enstratus cloud account that is the account under which
            the machine image is registered.

            .. .note::

                This value is empty for public images and in rare circumstances
                when enStratus is unable to determine the ownership

        """
        return self.__owning_cloud_account_number

    @lazy_property
    def owning_user(self):
        """`dict` or `None` - The user who is the owner of record of this machine image.

            .. .note::

                The owner may be null in cases of auto-discovery or certain automated scenarios

        """
        return self.__owning_user

    @lazy_property
    def owning_groups(self):
        """`list` - The groups who have ownership over this machine image"""
        return self.__owning_groups

    @lazy_property
    def platform(self):
        """`str` - The operating system bundled into the machine image/template"""
        return self.__platform

    @lazy_property
    def provider_id(self):
        """`str` - The cloud provider's unique id for the machine image"""
        return self.__provider_id

    @lazy_property
    def region(self):
        """`dict` - The region in which this machine image is available"""
        return self.__region

    @lazy_property
    def removable(self):
        """`bool` - Whether or not this machine image can be deleted"""
        return self.__removable

    @lazy_property
    def sharable(self):
        """`bool` - Whether or not this image can be shared"""
        return self.__sharable

    @lazy_property
    def status(self):
        """`str` - The current status of this machine image"""
        return self.__status

    @lazy_property
    def label(self):
        """`str` - A color label assigned to this machine image"""
        return self.__label

    @lazy_property
    def products(self):
        """`list` - The server products that can be used to provision a virtual
            machine based on this machine image/template
        """
        return self.__products

    @lazy_property
    def agent_version(self):
        """`int` - The version of the enStratus agent if installed on the machine image"""
        return self.__agent_version

    @classmethod
    def all(cls, region_id, **kwargs):
        """Return all machine images

        :param region_id: The region to search for machine images
        :type region_id: int.
        :param keys_only: Return :attr:`machine_image_id` instead of :class:`MachineImage`
        :type keys_only: bool.
        :param available: Return only available images. Default is `true`
        :type available: str.
        :param registered: Return only images with the enStratus agent installed. Default is `false`
        :type registered: str.
        :param detail: The level of detail to return - `basic` or `extended`
        :type detail: str.
        :returns: `list` of :class:`MachineImage` or :attr:`machine_image_id`
        :raises: :class:`MachineImageException`
        """
        r = Resource(cls.PATH)
        r.request_details = 'basic'
        params = {'regionId':region_id}
        if 'keys_only' in kwargs:
            keys_only = kwargs['keys_only']
        else:
            keys_only = False
        if 'available' in kwargs:
            params['active'] = kwargs['active']
        if 'registered' in kwargs:
            params['registered'] = kwargs['registered']
        c = r.get(params=params)
        if r.last_error is None:
            if keys_only is True:
                images = [item['machineImageId'] for item in c[cls.COLLECTION_NAME]]
            else:
                images = []
                for i in c[cls.COLLECTION_NAME]:
                    image = cls(i['machineImageId'])
                    if 'detail' in kwargs:
                        image.request_details = kwargs['detail']
                    image.load()
                    images.append(image)
            return images
        else:
            raise MachineImageException(r.last_error)

class MachineImageException(BaseException): pass
