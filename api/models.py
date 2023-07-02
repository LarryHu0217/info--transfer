from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    MinLengthValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.html import format_html


BABY_RELATION = [
    ("MOTHER", "Soy la mamá"),
    ("FATHER", "Soy el papá"),
    ("OTHER", "Otro"),
]

HEALTH_SECTOR = [
    ("PUBLIC", "Público - Fonasa"),
    ("PRIVATE", "Privado - Isapre"),
]

EDUCATION_LEVEL = [
    ("BASIC", "Educación Básica - hasta los 15 años"),
    ("MEDIUM", "Educación media - hasta los 18 años"),
    ("UNI_INCOMPLETE", "Educación universitaria o técnica incompleta"),
    ("UNI_COMPLETE", "Educación universitaria o técnica completa"),
]

NUMBER_OF_CHILDREN = [
    ("FIRST", "Es el primer bebé"),
    ("SECOND", "Es el segundo bebé"),
    ("THIRD", "Es el tercer bebé"),
    ("FOURTH", "Es el cuarto o más"),
]

SATISFACTION_LEVEL = [
    ("VERY_UNSATISFIED", "Extremadamente insatisfecha"),
    ("SOME_UNSATISFIED", "Algo insatisfecha"),
    ("NIETHER", "Ni satisfecha ni insatisfecha"),
    ("SOME_SATISFIED", "Algo satisfecha"),
    ("VERY_SATISFIED", "Extremadamente satisfecha"),
]

FREQUENCY_LEVEL = [
    ("VERY_MUCH", "Tanto como siempre"),
    ("MUCH", "No tanto ahora"),
    ("NOT_MUCH", "Mucho menos ahora"),
    ("NEVER", "No, nada"),
]

TIME_LEVEL = [
    ("MOST_OF_TIME", "Sí, la mayor parte del tiempo"),
    ("YES_SOMETIMES", "Sí, a veces"),
    ("NOT_OFTEN", "No con mucha frequencia"),
    ("NEVER", "No,nunca"),
]

FEELING_LEVEL = [
    ("FREQUENTLY", "Sí, con mucha frequencia"),
    ("SOMETIMES", "A veces"),
    ("ALMOST_NEVER", "Casi nunca"),
    ("NEVER", "Nunca"),
]

OVERWHELMED_LEVEL = [
    ("YES_MOST", "Sí, la mayor parte del tiempo no he podido hacer las cosas"),
    ("YES_SOMETIMES", "Sí, a veces no he podido hace las cosas tan bien como siempre"),
    ("NOT_OFTEN", "No, la mayor parte del tiempo he hecho las cosas bastante bien"),
    ("NEVER", "No, he estado haciendo las cosas tan bien como siempre"),
]


def email_validator(email):
    message = format_html(
        'Por favor usa el correo con el que te registraste o regístrate en nuestra <a href="{}">página</a>',
        "https://www.mi-tribu.cl/",
    )
    try:
        match = UserInformation.objects.get(email=email)
        return email
    except UserInformation.DoesNotExist:
        raise ValidationError(
            message,
            code="invalid",
        )


def user_already_filled_out_validator(email):
    message = format_html("Ha completado esta encuesta con este correo electrónico")
    if UserInformation.objects.filter(email=email).exists():
        raise ValidationError(
            message,
            code="invalid",
        )
    else:
        return email


class UserInformation(models.Model):
    first_name = models.CharField(
        max_length=50,
        unique=False,
    )
    has_completed_onboard= models.BooleanField(
        default=False,
        null=True,
        blank=True
    )
    otp_token=models.CharField(
        max_length=6,
        unique=False,
        null=True,
        blank=True,
    )
    otp_due_date=models.DateTimeField(
        null=True,
        blank=True,
        auto_now=False,
        auto_now_add=True
    )
    last_name = models.CharField(
        max_length=50,

        unique=False,
    )

    password = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        validators=[user_already_filled_out_validator],
    )
    phone = models.CharField(
        max_length=15,
        validators=[MinLengthValidator(limit_value=8)],
        null=True,
        blank=True,
    )
    last_period_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    pregnancy_week = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    pregnancy_week_round = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    subscription_date = models.DateField(null=True, blank=True)
    next_mailing_date = models.DateField(null=True, blank=True)
    welcome_survey_sending_date = models.DateField(null=True, blank=True)
    welcome_survey_reit_date = models.DateField(null=True, blank=True)
    welcome_filled = models.BooleanField(default=False)
    mid_survey_sending_date = models.DateField(null=True, blank=True)
    mid_survey_reit_date = models.DateField(null=True, blank=True)
    mid_filled = models.BooleanField(default=False)
    closing_survey_sending_date = models.DateField(null=True, blank=True)
    closing_survey_reit_date = models.DateField(null=True, blank=True)
    closing_filled = models.BooleanField(default=False)
    cancel_all = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)


def endinburgh_already_filled_out_validator(email):
    message = format_html("Ha completado esta encuesta con este correo electrónico")
    if EdinburghTest.objects.filter(email=email).exists():
        raise ValidationError(
            message,
            code="invalid",
        )
    else:
        return email


class EdinburghTest(models.Model):
    # 1. ¿Cuál es tu email? (que utilizas con Mi Tribu)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        validators=[email_validator, endinburgh_already_filled_out_validator],
    )
    # 2. En los últimos 7 días, he sido capaz de reírme y ver el lado divertido de las cosas:
    happy = models.CharField(
        max_length=50,
        choices=FREQUENCY_LEVEL,
    )
    # 3. En los últimos 7 días, he disfrutado mirar hacia delante:
    vision = models.CharField(
        max_length=50,
        choices=FREQUENCY_LEVEL,
    )
    # 4. En los últimos 7 días, cuando las cosas han salido mal, me he culpado a mi misma innecesariamente:
    self_blame = models.CharField(
        max_length=50,
        choices=TIME_LEVEL,
    )
    # 5. En los últimos 7 días, he estado nerviosa o inquieta sin tener motivo:
    nervous = models.CharField(
        max_length=50,
        choices=FEELING_LEVEL,
    )
    # 6. En los últimos 7 días, he sentido miedo o he estado asustadiza sin tener motivo:
    scared = models.CharField(
        max_length=50,
        choices=FEELING_LEVEL,
    )
    # 7. En los últimos 7 días, las cosas me han estado abrumando:
    overwhelmed = models.CharField(
        max_length=50,
        choices=OVERWHELMED_LEVEL,
    )
    # 8. En los últimos 7 días, me he sentido tan desdichada que he tenido dificultades para dormir:
    sleepless = models.CharField(
        max_length=50,
        choices=TIME_LEVEL,
    )
    # 9. En los últimos 7 días, me he sentido triste o desgraciada:
    sad = models.CharField(
        max_length=50,
        choices=TIME_LEVEL,
    )
    # 10. En los últimos 7 días, me he sentido tan desdichada que he estado llorando:
    cried = models.CharField(
        max_length=50,
        choices=TIME_LEVEL,
    )
    # 11. En los últimos 7 días, se me ha ocurrido la idea de hacerme daño:
    harm = models.CharField(
        max_length=50,
        choices=FEELING_LEVEL,
    )


def closing_already_filled_out_validator(email):
    message = format_html("Ha completado esta encuesta con este correo electrónico")
    if ClosingSurvey.objects.filter(email=email).exists():
        raise ValidationError(
            message,
            code="invalid",
        )
    else:
        return email


class ClosingSurvey(models.Model):
    # 1. ¿Cuál es tu email? (que utilizas con Mi Tribu)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        validators=[email_validator, closing_already_filled_out_validator],
    )
    # 2. ¿Qué nivel de satisfacción te están dando cada una de las secciones de los emails semanales?
    # - 1. Estado de tu embarazo (tu cuerpo, tu bebé, tus síntomas)
    symptoms = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 2. Tips
    tips = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 3. Meme
    meme = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 4. Preguntas frecuentes
    frequent_questions = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 5. Encuesta semanal
    weekly_survey = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # 3. En una escala de 0 a 10, ¿qué tan probable es que recomiendes a Mi Tribu a una amiga o conocida?
    recommendation = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=10),
        ],
    )
    # 4. En general, ¿qué te faltó en tu proceso del embarazo?
    missing = models.CharField(
        max_length=255,
        unique=False,
    )
    # 5. Estamos empezando a recolectar consejos de madres para madres. ¿Quieres compartir un consejo con la comunidad de futuras madres de Mi Tribu que vienen después de ti?
    advice = models.CharField(
        max_length=255,
        unique=False,
    )


def mid_already_filled_out_validator(email):
    message = format_html("Ha completado esta encuesta con este correo electrónico")
    if MidSurvey.objects.filter(email=email).exists():
        raise ValidationError(
            message,
            code="invalid",
        )
    else:
        return email


class MidSurvey(models.Model):
    # 1. ¿Cuál es tu email? (que utilizas con Mi Tribu)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        validators=[email_validator, mid_already_filled_out_validator],
    )
    # 2. ¿Qué nivel de satisfacción te están dando cada una de las secciones de los emails semanales?
    # - 1. Estado de tu embarazo (tu cuerpo, tu bebé, tus síntomas)
    symptoms = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 2. Tips
    tips = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 3. Meme
    meme = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 4. Preguntas frecuentes
    frequent_questions = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # - 5. Encuesta semanal
    weekly_survey = models.CharField(
        max_length=50,
        choices=SATISFACTION_LEVEL,
    )
    # 3. En una escala de 0 a 10, ¿qué tan probable es que recomiendes a Mi Tribu a una amiga o conocida?
    recommendation = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=10),
        ],
    )
    # 4. Actualmente estamos desarrollando diferentes funcionalidades y nos gustaría saber qué te interesa que prioricemos para ti.
    # - Programa integral de clases pre-natales y post-natales impartidos online por profesionales con diferentes especialidades.
    program_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Marketplace para la compra, venta y donación de productos de bebé de segunda mano.
    marketplace_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Aplicación móvil con contenido personalizado para ti junto a herramientas como seguimiento de peso, contador de contracciones, y ejercicios de piso pélvico.
    health_app_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Chat grupal 24/7 de 3-7 madres en el mismo mes de embarazo con una guía.
    mom_chat_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Registro o Lista de Bebé con los artículos que necesitarás comprar para tu bebé con el cual amigos/familia puedan comprarlas por ti (similar a Lista de Novios).
    registry_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Foro abierto de mamás de Mi Tribu para preguntar y comentar sobre lo que quieras o necesites.
    forum_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Chat privado para preguntas cortas a profesionales de salud.
    professional_chat_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Plataforma digital para reservar consultas por videollamadas online 1:1 con profesionales de salud.
    digital_platform_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )
    # - Aplicación móvil con clases pre-grabadas de ejercicios pre- y post-natales tipo Yoga, Meditación y Pilates.
    workout_app_rank = models.IntegerField(
        validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=9)],
    )


def welcome_already_filled_out_validator(email):
    message = format_html("Ha completado esta encuesta con este correo electrónico")
    if WelcomeSurvey.objects.filter(email=email).exists():
        raise ValidationError(
            message,
            code="invalid",
        )
    else:
        return email


class WelcomeSurvey(models.Model):
    # 1. ¿Cuál es tu email? (que utilizas con Mi Tribu)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        validators=[email_validator, welcome_already_filled_out_validator],
    )
    # 2. ¿Cuál es tu relación con el bebé?
    relation_to_baby = models.CharField(
        max_length=50,
        choices=BABY_RELATION,
    )
    # 3 ¿Dónde vives?
    # - País
    country = models.CharField(
        max_length=100,
        unique=False,
    )
    # - Ciudad
    city = models.CharField(
        max_length=100,
        unique=False,
    )
    # Comuna
    commune = models.CharField(
        max_length=100,
        unique=False,
    )
    # 4. ¿Te atiendes principalmente en el sector público o privado?
    sector = models.CharField(
        verbose_name="health sector",
        max_length=50,
        choices=HEALTH_SECTOR,
    )
    # 5. ¿Cuántos años tienes?
    age = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=13),
            MaxValueValidator(limit_value=100),
        ],
        blank=True,
        null=True,
    )
    # 6. ¿Cuál es el nivel más alto de educación que has completado?
    education = models.CharField(
        verbose_name="highest education level",
        max_length=50,
        choices=EDUCATION_LEVEL,
    )
    # 7. ¿Qué número de hijo o hija es el que estás esperando?
    num_children = models.CharField(
        verbose_name="number of children",
        max_length=50,
        choices=NUMBER_OF_CHILDREN,
    )
    # 8. ¿De dónde has obtenido información acerca de tu embarazo? Selecciona todas las que has utilizado.
    # - Profesional de la salud (médico, matrona, enfermera, kinesióloga, etc)
    professional_health = models.BooleanField(default=False)
    # - Libros
    books = models.BooleanField(default=False)
    # - E-mails de suscripción
    emails = models.BooleanField(default=False)
    # - Blogs de internet
    blogs = models.BooleanField(default=False)
    # - Redes sociales (Instagram, Facebook, Pinterest)
    social_media = models.BooleanField(default=False)
    # - Cursos / Charlas / Talleres online
    online_courses = models.BooleanField(default=False)
    # - Cursos / Charlas / Talleres presenciales
    in_person_courses = models.BooleanField(default=False)
    # - Applicaciones móviles
    mobile_apps = models.BooleanField(default=False)
    # - Otro
    # other = models.BooleanField(default=False)
    other_information = models.CharField(
        max_length=255,
        unique=False,
        null=True,
        blank=True,
    )
    # 9. ¿Cómo supiste de Mi Tribu?
    find_us_out = models.CharField(
        max_length=255,
        unique=False,
    )
#
# token
# email_validator
# day# foreign key/ email /token