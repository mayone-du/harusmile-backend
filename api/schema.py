from datetime import timedelta

import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.signing import BadSignature, dumps, loads
from django.db.models import Q
from django.http import HttpResponseBadRequest
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .models import (Address, Gender, Message, Notification, Plan, Profile,
                     Review, Tag, TalkRoom, User)


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
            # 本人確認が済んでいるユーザーをフィルタリング
            'target_user__is_active': ['exact'],

            'profile_name': ['exact', 'icontains'],
            'profile_text': ['exact', 'icontains'],
            'age': ['exact'],
            'is_college_student': ['exact'],
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


class PlanNode(DjangoObjectType):
    class Meta:
        model = Plan
        filter_fields = {
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
            'is_published': ['exact'],
            'price': ['exact']
        }
        interfaces = (relay.Node,)


class TalkRoomNode(DjangoObjectType):
    class Meta:
        model = TalkRoom
        filter_fields = {
            # 'join_users': ['exact', 'icontains'],
            'selected_plan': ['exact'],
        }
        interfaces = (relay.Node,)


class MessageNode(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = {
            'text': ['exact', 'icontains'],
            # 'talking_room__join_users': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class ReviewNode(DjangoObjectType):
    class Meta:
        model = Review
        filter_fields = {
            'stars': ['exact'],
            'review_text': ['exact', 'icontains'],
            'customer_id': ['exact']
        }
        interfaces = (relay.Node,)


class NotificationNode(DjangoObjectType):
    class Meta:
        model = Notification
        filter_fields = {
            'is_checked': ['exact'],
            'receiver': ['exact']
        }
        interfaces = (relay.Node,)

# ユーザー作成
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
        # userのpkをもとに暗号化
        token = dumps(user.pk)
        # メールの有効期限を設定
        # TODO: フロント側で有効期限ないか確認 新規登録はしたが期限が切れた場合にメールを再送する設定も。
        exp = timedelta(minutes=30)
        # TODO: クエリパラメーターでemailとpasswordをおくり、ログインの処理もさせる？
        # http://localhost:3000/auth/verify?token={token}&email={input.get('email')}&password={input.get('password')}
        html_message = f'''
        <h1>ユーザー作成時にメール送信しています</h1>\n
                <p><a href="http://localhost:3000/auth/verify?token={token}&exp={exp}">こちらのリンク</a>をクリックして本登録をしてください。</p>
                    '''
        # 作成されたメールアドレスに対してメールを送信
        send_mail(subject='ハルスマイル | 本登録のご案内', message="本登録のご案内です。", html_message=html_message, from_email="harusmile@email.com",
                recipient_list=[input.get('email')], fail_silently=False)

        return CreateUserMutation(user=user)
        


# ユーザーの更新（メールから本人確認）
class UpdateUserMutation(relay.ClientIDMutation):
    class Input:
        token = graphene.String(required=True)
    
    ok = graphene.Boolean()

    def mutate_and_get_payload(root, info, token):
        # TODO: 他の箇所もトランザクション化したり、↓がこのままで大丈夫か確認 エラーハンドリングを丁寧に設定
        try:
            # tokenからユーザーのpkを復号
            user_pk = loads(token)
            # ユーザーを取得
            user = get_user_model().objects.get(pk=user_pk)
        # tokenが間違っている場合
        except BadSignature:
            raise HttpResponseBadRequest()
        # ユーザーが存在しない場合
        except User.DoesNotExist:
            raise HttpResponseBadRequest()
        # ユーザーの本登録がまだであれば本登録のフラグをTrueに更新する
        if not user.is_active:
            user.is_active = True
            user.save()
            ok = True
            return UpdateUserMutation(ok=ok)
        # 既に本登録済みの場合
        else:
            raise HttpResponseBadRequest()



# プロフィールの作成
class CreateProfileMutation(relay.ClientIDMutation):
    class Input:
        # ↓メールアドレスでの認証を挟むため引数で取得
        target_user_id=graphene.ID(required=True)
        profile_name = graphene.String(required=True)
        profile_text = graphene.String(required=False)
        is_college_student = graphene.Boolean(required=True)
        school_name = graphene.String(required=True)
        age = graphene.Int(required=False)
        selected_gender = graphene.ID(required=False)
        selected_address = graphene.ID(required=False)
        telephone_number = graphene.String(required=False)
        want_hear = graphene.String(required=False)
        problem = graphene.String(required=False)
        undergraduate = graphene.String(required=False)
        department = graphene.String(required=False)
        club_activities = graphene.String(required=False)
        admission_format = graphene.String(required=False)
        favorite_subject = graphene.String(required=False)
        profile_image = Upload(required=False)

    profile = graphene.Field(ProfileNode)

    # @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            # target_user_id=info.context.user.id,
            target_user_id=from_global_id(input.get('target_user_id'))[1],
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
            profile_image=input.get('profile_image'),
        )
        profile.save()
        return CreateProfileMutation(profile=profile)

# プロフィールの更新
class UpdateProfileMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        profile_name = graphene.String(required=True)
        profile_text = graphene.String(required=False)
        is_college_student = graphene.Boolean(required=False)
        school_name = graphene.String(required=False)
        age = graphene.Int(required=False)
        selected_gender = graphene.ID(required=True)
        selected_address = graphene.ID(required=True)
        telephone_number = graphene.String(required=False)
        want_hear = graphene.String(required=False)
        problem = graphene.String(required=False)
        following_users = graphene.List(graphene.ID)
        tags = graphene.List(graphene.ID)
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
            # profile_image=input.get('profile_image'),
        )

        # プロフィール画像が設定されていなかったら以前のまま更新しない
        if input.get('profile_image') is not None:
            profile.profile_image = input.get('profile_image')
        else:
            my_profile = Profile.objects.get(
                id=from_global_id(input.get('id'))[1])
            profile.profile_image = my_profile.profile_image

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


# プランの作成
class CreatePlanMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        plan_image = Upload(required=False)
        is_published = graphene.Boolean(required=True)
        price = graphene.Int(required=True)

    plan = graphene.Field(PlanNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        plan = Plan(
            plan_author_id=info.context.user.id,
            title=input.get('title'),
            content=input.get('content'),
            plan_image=input.get('plan_image'),
            price=input.get('price'),
            is_published=input.get('is_published'),
        )
        plan.save()

        return CreatePlanMutation(plan=plan)

# プランの更新
class UpdatePlanMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        plan_image = Upload(required=False)
        price = graphene.Int(required=True)
        is_published = graphene.Boolean(required=True)

    plan = graphene.Field(PlanNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        plan = Plan(
            id=from_global_id(input.get('id'))[1],
            title=input.get('title'),
            content=input.get('content'),
            price=input.get('price'),
            is_published=input.get('is_published'),
        )

        if input.get('plan_image') is not None:
            plan.plan_image = input.get('plan_image')
        else:
            selected_plan = Plan.objects.get(
                id=from_global_id(input.get('id'))[1])
            plan.plan_image = selected_plan.plan_image

        plan.save()
        return UpdatePlanMutation(plan=plan)

# プランの削除
class DeletePlanMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    plan = graphene.Field(PlanNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        plan = Plan(
            id=from_global_id(input.get('id'))[1],
        )
        plan.delete()
        return DeletePlanMutation(plan=plan)


# トークルーム作成用
class CreateTalkRoomMutation(relay.ClientIDMutation):
    class Input:
        talk_room_description = graphene.String(required=False)
        # join_users = graphene.List(graphene.ID)
        selected_plan = graphene.ID(required=True)
        opponent_user = graphene.ID(required=True)

    talk_room = graphene.Field(TalkRoomNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        talk_room = TalkRoom(
            talk_room_description=input.get('talk_room_description'),
            # ! ↓TalkRoomモデルのフィールドのそれぞれの外部キーに、各modelインスタンスのキーを設定する
            selected_plan_id=from_global_id(input.get('selected_plan'))[1],
            opponent_user_id=from_global_id(input.get('opponent_user'))[1],
        )
        # ManyToMany時は↓で一旦saveが必要
        talk_room.save()

        # if input.get('join_users') is not None:
        #     join_users_set = []
        #     for join_user in input.get('join_users'):
        #         join_user_id = from_global_id(join_user)[1]
        #         join_user_object = User.objects.get(id=join_user_id)
        #         join_users_set.append(join_user_object)
        #         talk_room.join_users.set(join_users_set)
        #     talk_room.save()

        # talk_room.save()
        return CreateTalkRoomMutation(talk_room=talk_room)

# トークルームの更新
class UpdateTalkRoomMutation(relay.ClientIDMutation):
    class Input:
        talk_room_id = graphene.ID(reuquired=True)
        is_approve = graphene.Boolean(required=True)

    talk_room = graphene.Field(TalkRoomNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        talk_room = TalkRoom.objects.get(
            id=from_global_id(input.get('talk_room_id'))[1],
        )
        # 承認フラグをTrueに更新
        talk_room.is_approve = input.get('is_approve')
        # talk_room.talk_room_description = TalkRoom.get(
        #     id=from_global_id(input.get('talk_room_id'))[1]).description
        talk_room.save()
        return UpdateTalkRoomMutation(talk_room=talk_room)


# メッセージ作成
class CreateMessageMutation(relay.ClientIDMutation):
    class Input:
        talking_room_id = graphene.ID(required=True)
        text = graphene.String(required=True)

    message = graphene.Field(MessageNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        message = Message(
            text=input.get('text'),
            talking_room_id=from_global_id(input.get('talking_room_id'))[1],
            sender_id=info.context.user.id,
        )
        message.save()
        return CreateMessageMutation(message=message)

# レビューの作成
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
            provider_id=from_global_id(input.get('provider'))[1],
            customer_id=info.context.user.id,
            review_text=input.get('review_text'),
            stars=input.get('stars'),
        )
        review.save()
        return CreateReviewMutation(review=review)

# 通知の作成
class CreateNotificationMutation(relay.ClientIDMutation):
    class Input:
        receiver = graphene.ID(required=True)
        notification_type = graphene.String(required=True)

    notification = graphene.Field(NotificationNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        notification = Notification(
            is_checked=False,
            notificator_id=info.context.user.id,
            receiver_id=from_global_id(input.get('receiver'))[1],
            notification_type=input.get('notification_type')
        )

        notification.save()
        return CreateNotificationMutation(notification=notification)

# 通知を更新
class UpdateNotificationsMutation(relay.ClientIDMutation):
    # リスト形式でIDを受け取る
    class Input:
        notification_ids = graphene.List(graphene.ID)

    notification = graphene.Field(NotificationNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        notification = Notification()
        if input.get('notification_ids') is not None:
            for notification_id in input.get('notification_ids'):
                notification = ''
                notification_object = Notification.objects.get(
                    id=from_global_id(notification_id)[1])
                # チェックしたかのフラグをTrueに更新
                notification_object.is_checked = True
                notification_object.notificator_id = notification_object.notificator_id
                notification_object.receiver_id = notification_object.receiver_id
                notification = notification_object
                notification.save()
        notification.save()
        return UpdateNotificationsMutation(notification=notification)


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    update_user = UpdateUserMutation.Field()
    create_profile = CreateProfileMutation.Field()
    update_profile = UpdateProfileMutation.Field()

    create_plan = CreatePlanMutation.Field()
    update_plan = UpdatePlanMutation.Field()
    delete_plan = DeletePlanMutation.Field()

    create_talk_room = CreateTalkRoomMutation().Field()
    update_talk_room = UpdateTalkRoomMutation().Field()
    create_message = CreateMessageMutation.Field()

    create_review = CreateReviewMutation.Field()

    create_notification = CreateNotificationMutation.Field()
    update_notifications = UpdateNotificationsMutation.Field()

    # python manage.py cleartokens コマンドで無効なtokenを削除できる
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


class Query(graphene.ObjectType):
    login_user = graphene.Field(UserNode)
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)
    profile = graphene.Field(ProfileNode, id=graphene.NonNull(graphene.ID))
    all_profiles = DjangoFilterConnectionField(ProfileNode)
    high_school_profiles = DjangoFilterConnectionField(ProfileNode)
    college_profiles = DjangoFilterConnectionField(ProfileNode)
    plan = graphene.Field(PlanNode, id=graphene.NonNull(graphene.ID))
    all_plans = DjangoFilterConnectionField(PlanNode)
    login_user_plans = DjangoFilterConnectionField(PlanNode)
    tag = graphene.Field(TagNode, id=graphene.NonNull(graphene.ID))
    all_tags = DjangoFilterConnectionField(TagNode)
    review = graphene.Field(ReviewNode, id=graphene.NonNull(graphene.ID))
    all_reviews = DjangoFilterConnectionField(ReviewNode)
    login_user_reviews = DjangoFilterConnectionField(ReviewNode)
    login_user_send_reviews = DjangoFilterConnectionField(ReviewNode)
    # login_user_written_reviews = DjangoFilterConnectionField(ReviewNode)
    gender = graphene.Field(GenderNode, id=graphene.NonNull(graphene.ID))
    all_genders = DjangoFilterConnectionField(GenderNode)
    address = graphene.Field(AddressNode, id=graphene.NonNull(graphene.ID))
    all_addresses = DjangoFilterConnectionField(AddressNode)
    talk_room = graphene.Field(TalkRoomNode, id=graphene.NonNull(graphene.ID))
    all_talk_rooms = DjangoFilterConnectionField(TalkRoomNode)
    login_user_talk_rooms = DjangoFilterConnectionField(TalkRoomNode)
    message = graphene.Field(MessageNode, id=graphene.NonNull(graphene.ID))
    all_messages = DjangoFilterConnectionField(MessageNode)
    login_user_messages = DjangoFilterConnectionField(MessageNode)
    notification = graphene.Field(
        NotificationNode, id=graphene.NonNull(graphene.ID))
    login_user_notifications = DjangoFilterConnectionField(NotificationNode)

    # login_user

    # 自分のプロフィールを取得
    # @login_required
    def resolve_login_user(self, info, **kwargs):
        return User.objects.get(id=info.context.user.id)

    # user

    # ユーザーを取得
    @login_required
    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return get_user_model().objects.get(id=from_global_id(id)[1])

    # すべてのユーザーを取得
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

    # high_school_profiles
    def resolve_high_school_profiles(self, info, **kwargs):
        return Profile.objects.filter(is_college_student=False)
    # college_profiles

    def resolve_college_profiles(self, info, **kwargs):
        return Profile.objects.filter(is_college_student=True)

    # plan
    def resolve_plan(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Plan.objects.get(id=from_global_id(id)[1])

    def resolve_all_plans(self, info, **kwargs):
        return Plan.objects.all()

    def resolve_login_user_plans(self, info, **kwargs):
        return Plan.objects.filter(plan_author=info.context.user.id)

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
    # login_required
    def resolve_review(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Review.objects.get(id=from_global_id(id)[1])

    # login_required
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

    @login_required
    def resolve_login_user_talk_rooms(self, info, **kwargs):
        return TalkRoom.objects.filter(Q(selected_plan__plan_author=info.context.user.id) | Q(opponent_user=info.context.user.id))

    # login_required
    # 自分が受け取ったレビュー
    def resolve_login_user_reviews(self, info, **kwargs):
        return Review.objects.filter(provider=info.context.user.id)

    # 自分が送信したレビュー
    def resolve_login_user_send_reviews(self, info, **kwargs):
        return Review.objects.filter(customer=info.context.user.id)

    # def resolve_login_user_written_reviews(self, info, **kwargs):
    #     return Review.objects.filter(customer=info.context.user.id)

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

    @login_required
    def resolve_notification(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Notification.objects.get(id=from_global_id(id)[1])

    # @login_required
    def resolve_login_user_notifications(self, info, **kwargs):
        return Notification.objects.filter(receiver=info.context.user.id)
