from typing import Text
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from .models import User, Tag, Profile, Post, Review, Message, Address, Gender, TalkRoom
from graphene_file_upload.scalars import Upload


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'email': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        filter_fields = {
            'tag_name': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class GenderNode(DjangoObjectType):
    class Meta:
        model = Gender
        filter_fields = {
            'gender_name': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class AddressNode(DjangoObjectType):
    class Meta:
        model = Address
        filter_fields = {
            'address_name': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'profile_name': ['exact', 'icontains'],
            'profile_text': ['exact', 'icontains'],
            'age': ['exact'],
            'is_college_student': ['exact', ],
            'school_name': ['exact', 'icontains'],

            'undergraduate': ['exact', 'icontains'],
            'department': ['exact', 'icontains'],
            'club_activities': ['exact', 'icontains'],
            'admission_format': ['exact', 'icontains'],
            'favorite_subject': ['exact', 'icontains'],
            'want_hear': ['exact', 'icontains'],
            'problem': ['exact', 'icontains'],

            'selected_address': ['exact'],
            'selected_gender': ['exact'],
        }
        interfaces = (relay.Node,)


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        filter_fields = {
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class TalkRoomNode(DjangoObjectType):
    class Meta:
        model = TalkRoom
        filter_fields = {
            'join_users': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class MessageNode(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = {
            'text': ['exact', 'icontains'],
            'talking_room__join_users': ['exact', 'icontains'],
            # 'text': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class ReviewNode(DjangoObjectType):
    class Meta:
        model = Review
        filter_fields = {
            'stars': ['exact'],
            'review_text': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class CreateUserMutation(relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = User(
            email=input.get('email'),
        )
        user.set_password(input.get('password'))
        user.save()

        return CreateUserMutation(user=user)


class CreateProfileMutation(relay.ClientIDMutation):
    class Input:
        profile_name = graphene.String(required=True)
        profile_text = graphene.String(required=False)
        is_college_student = graphene.Boolean(required=True)
        school_name = graphene.String(required=True)
        age = graphene.Int(required=False)
        selected_gender = graphene.ID(required=True)
        selected_address = graphene.ID(required=True)
        telephone_number = graphene.String(required=True)
        want_hear = graphene.String(required=False)
        problem = graphene.String(required=False)
        undergraduate = graphene.String(required=False)
        department = graphene.String(required=False)
        club_activities = graphene.String(required=False)
        admission_format = graphene.String(required=False)
        favorite_subject = graphene.String(required=False)
        profile_image = Upload(required=False)

    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            target_user_id=info.context.user.id,
            profile_name=input.get('profile_name'),
            profile_text=input.get('profile_text'),
            is_college_student=input.get('is_college_student'),
            school_name=input.get('school_name'),
            age=input.get('age'),
            undergraduate=input.get('undergraduate'),
            department=input.get('department'),
            club_activities=input.get('club_activities'),
            admission_format=input.get('admission_format'),
            favorite_subject=input.get('favorite_subject'),
            telephone_number=input.get('telephone_number'),
            want_hear=input.get('want_hear'),
            problem=input.get('problem'),
            selected_gender=Gender.objects.get(
                id=from_global_id(input.get('selected_gender'))[1]),
            selected_address=Address.objects.get(
                id=from_global_id(input.get('selected_address'))[1]),
            profile_image=input.get('profile_image'),
        )
        profile.save()

        return CreateProfileMutation(profile=profile)


class UpdateProfileMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        profile_name = graphene.String(required=True)
        profile_text = graphene.String(required=True)
        is_college_student = graphene.Boolean(required=True)
        school_name = graphene.String(required=True)
        age = graphene.Int(required=True)
        selected_gender = graphene.ID(required=True)
        selected_address = graphene.ID(required=True)
        telephone_number = graphene.String(required=True)
        want_hear = graphene.String(required=True)
        problem = graphene.String(required=True)
        following_users = graphene.List(graphene.ID)
        tags = graphene.List(graphene.ID)
        undergraduate = graphene.String(required=True)
        department = graphene.String(required=True)
        club_activities = graphene.String(required=True)
        admission_format = graphene.String(required=True)
        favorite_subject = graphene.String(required=True)
        profile_image = Upload(required=False)

    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            target_user_id=info.context.user.id,
            id=from_global_id(input.get('id'))[1],
            profile_name=input.get('profile_name'),
            profile_text=input.get('profile_text'),
            is_college_student=input.get('is_college_student'),
            school_name=input.get('school_name'),
            age=input.get('age'),
            undergraduate=input.get('undergraduate'),
            department=input.get('department'),
            club_activities=input.get('club_activities'),
            admission_format=input.get('admission_format'),
            favorite_subject=input.get('favorite_subject'),
            telephone_number=input.get('telephone_number'),
            want_hear=input.get('want_hear'),
            problem=input.get('problem'),
            selected_gender=Gender.objects.get(
                id=from_global_id(input.get('selected_gender'))[1]),
            selected_address=Address.objects.get(
                id=from_global_id(input.get('selected_address'))[1]),
            profile_image=input.get('profile_image'),
        )

        if input.get('following_users') is not None:
            followings_set = []
            for user in input.get('following_users'):
                followings_id = from_global_id(user)[1]
                user_object = User.objects.get(id=followings_id)
                followings_set.append(user_object)
                profile.followings.set(followings_set)
            profile.save()

        if input.get('tags') is not None:
            tag_set = []
            for tag in input.get('tags'):
                tag_id = from_global_id(tag)[1]
                tag_object = Tag.objects.get(id=tag_id)
                tag_set.append(tag_object)
                profile.tags.set(tag_set)
            profile.save()
        profile.save()

        return UpdateProfileMutation(profile=profile)


class CreatePostMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        post_image = Upload(required=False)
        is_published = graphene.Boolean(required=True)

    post = graphene.Field(PostNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        post = Post(
            posted_user_id=info.context.user.id,
            title=input.get('title'),
            content=input.get('content'),
            post_image=input.get('post_image'),
            is_published=input.get('is_published'),
        )
        post.save()

        return CreatePostMutation(post=post)


class UpdatePostMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        title = graphene.String(required=False)
        content = graphene.String(required=False)
        post_image = Upload(required=False)
        is_published = graphene.Boolean(required=False)

    post = graphene.Field(PostNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        post = Post(
            id=from_global_id(input.get('id'))[1],
            title=input.get('title'),
            content=input.get('content'),
            post_image=input.get('post_image'),
            is_published=input.get('is_published'),
        )
        post.save()
        return UpdatePostMutation(post=post)


class DeletePostMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    post = graphene.Field(PostNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        post = Post(
            id=from_global_id(input.get('id'))[1],
        )
        post.delete()
        return DeletePostMutation(post=post)


# トークルーム作成用
class CreateTalkRoomMutation(relay.ClientIDMutation):
    class Input:
        talk_room_description = graphene.String(required=False)
        join_users = graphene.List(graphene.ID)

    talk_room = graphene.Field(TalkRoomNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        talk_room = TalkRoom(
            talk_room_description=input.get('talk_room_description'),
        )
        # ManyToMany時は↓で一旦saveが必要
        talk_room.save()

        if input.get('join_users') is not None:
            join_users_set = []
            for join_user in input.get('join_users'):
                join_user_id = from_global_id(join_user)[1]
                join_user_object = User.objects.get(id=join_user_id)
                join_users_set.append(join_user_object)
                talk_room.join_users.set(join_users_set)
            talk_room.save()

        talk_room.save()
        return CreateTalkRoomMutation(talk_room=talk_room)


# メッセージ作成
class CreateMessageMutation(relay.ClientIDMutation):
    class Input:
        talking_room_id = graphene.ID(required=True)
        text = graphene.String(required=True)

    message = graphene.Field(MessageNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        message = Message(
            text = input.get('text'),
            talking_room_id=from_global_id(input.get('talking_room_id'))[1],
            sender_id=info.context.user.id,
        )
        message.save()
        return CreateMessageMutation(message=message)


class CreateReviewMutation(relay.ClientIDMutation):
    class Input:
        # target_post = graphene.ID(required=True)
        provider = graphene.ID(required=True)
        review_text = graphene.String(required=True)
        stars = graphene.Int(required=True)

    review = graphene.Field(ReviewNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        review = Review(
            provider=from_global_id(input.get('provider'))[1],
            reviewed_user_id=info.context.user.id,
            review_text=input.get('review_text'),
            stars=input.get('stars'),
        )
        review.save()
        return CreateReviewMutation(review=review)


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    create_profile = CreateProfileMutation.Field()
    update_profile = UpdateProfileMutation.Field()

    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()

    create_talk_room = CreateTalkRoomMutation().Field()
    create_message = CreateMessageMutation.Field()

    create_review = CreateReviewMutation.Field()

    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


class Query(graphene.ObjectType):
    login_user = graphene.Field(UserNode)
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)
    profile = graphene.Field(ProfileNode, id=graphene.NonNull(graphene.ID))
    all_profiles = DjangoFilterConnectionField(ProfileNode)
    post = graphene.Field(PostNode, id=graphene.NonNull(graphene.ID))
    all_posts = DjangoFilterConnectionField(PostNode)
    tag = graphene.Field(TagNode, id=graphene.NonNull(graphene.ID))
    all_tags = DjangoFilterConnectionField(TagNode)
    review = graphene.Field(ReviewNode, id=graphene.NonNull(graphene.ID))
    all_reviews = DjangoFilterConnectionField(ReviewNode)
    gender = graphene.Field(GenderNode, id=graphene.NonNull(graphene.ID))
    all_genders = DjangoFilterConnectionField(GenderNode)
    address = graphene.Field(AddressNode, id=graphene.NonNull(graphene.ID))
    all_addresses = DjangoFilterConnectionField(AddressNode)
    talk_room = graphene.Field(TalkRoomNode, id=graphene.NonNull(graphene.ID))
    all_talk_rooms = DjangoFilterConnectionField(TalkRoomNode)
    message = graphene.Field(MessageNode, id=graphene.NonNull(graphene.ID))
    all_messages = DjangoFilterConnectionField(MessageNode)
    login_user_messages = DjangoFilterConnectionField(MessageNode)

    # login_user

    @login_required
    def resolve_login_user(self, info, **kwargs):
        return User.objects.get(id=info.context.user.id)

    # user

    @login_required
    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
          return get_user_model().objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    # profile
    def resolve_profile(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Profile.objects.get(id=from_global_id(id)[1])

    def resolve_all_profiles(self, info, **kwargs):
        return Profile.objects.all()

    # post
    def resolve_post(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Post.objects.get(id=from_global_id(id)[1])

    def resolve_all_posts(self, info, **kwargs):
        return Post.objects.all()

    # gender

    def resolve_gender(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Gender.objects.get(id=from_global_id(id)[1])

    def resolve_all_genders(self, info, **kwargs):
        return Gender.objects.all()

    # address

    def resolve_address(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Address.objects.get(id=from_global_id(id)[1])

    def resolve_all_addresses(self, info, **kwargs):
        return Address.objects.all()

    # tag
    @login_required
    def resolve_tag(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Tag.objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_tags(self, info, **kwargs):
        return Tag.objects.all()

    # review
    @login_required
    def resolve_review(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Review.objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_reviews(self, info, **kwargs):
        return Review.objects.all()

    # talk_room
    @login_required
    def resolve_talk_room(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return TalkRoom.objects.get(id=from_global_id(id)[1])


    @login_required
    def resolve_all_talk_rooms(self, info, **kwargs):
        return TalkRoom.objects.all()

    # message
    @login_required
    def resolve_message(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Message.objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_messages(self, info, **kwargs):
        return Message.objects.all()

    @login_required
    def resolve_login_user_messages(self, info, **kwargs):
        return Message.objects.filter(sender=info.context.user.id)

    
