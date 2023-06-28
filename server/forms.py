import math
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (
    StringField,
    FloatField,
    TextAreaField,
    BooleanField,
    IntegerField,
    PasswordField,
    EmailField,
    DateField,
    MultipleFileField
)
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    Email,
    NumberRange,
)
from wtforms import ValidationError


class LoginForm(FlaskForm):
    '''로그인 폼'''
    user_id = StringField(
        '사용자 아이디(최소 4글자)',
        validators=[DataRequired('아이디는 필수 입력 사항입니다.'), Length(min=4, max=25)]
    )
    passwd = PasswordField(
        '비밀번호',
        validators=[DataRequired('비번은 필수입력 사항입니다.')]
    )


class SignUpForm(FlaskForm):
    '''회원가입 폼'''
    user_id = StringField(
        '사용자 아이디',
        validators=[DataRequired('사용자 아이디는 반드시 입력해야 합니다.'), Length(min=3, max=25)]
    )
    passwd1 = PasswordField(
        '비밀번호',
        validators=[DataRequired('비밀번호는 반드시 입력해야 합니다.'), EqualTo('passwd2', '비밀번호가 일치하지 않습니다.')],
    )
    passwd2 = PasswordField('비밀번호', validators=[DataRequired('비밀번호 확인은 필수입니다.')])
    name = StringField(
        '이름(성 포함)',
        validators=[DataRequired('이름은 필수입력 사항입니다.'), Length(min=2, max=25)]
    )
    phone_mobile = StringField(
        '휴대전화 번호',
        validators=[DataRequired('휴대전화 번호는 필수사항입니다. 향후 추가인증을 위해 사용됩니다.'), ]
    )
    email = EmailField(
        '이메일',
        validators=[DataRequired('이메일은 필수입력 사항입니다.'), Email()],
    )


class TransferForm(FlaskForm):
    '''코인 이체 입력 폼'''
    amount = FloatField(
        label='이체 수량',
        validators = [
            DataRequired('코인 이체 수량 필수입력 사항입니다.'),
            NumberRange(min=0.000000001),
        ]
    )
    private_key = StringField(
        label='본인의 비밀키(Private Key)',
        validators=[
            DataRequired('블록체인 전송을 위해서는 본인의 비밀키가 반드시 있어야 합니다.'),
        ]
    )
    public_key = StringField(
        label='본인의 공개키(Public Key)',
        validators=[
            DataRequired('블록체인 전송을 위해서는 본인의 공개키가 반드시 있어야 합니다.'),
        ]
    )
    recv_addr = StringField(
        label='받는사람 지갑 주소',
        validators=[
            DataRequired('받는사람 지갑 주소는 필수입력 사항입니다.'),
        ]
    )