from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, UserUpdateSerializer, AddAddressSerializer,SubscriberSerializer
)
from .utils import send_html_mail
from .models import Users

def home(request):
    return HttpResponse("<h1>Hello world</h1>")


@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([AllowAny])
def contact_us_for_project(request):
    data = request.data

    name = data.get('name')
    email = data.get('email')
    msg = data.get('msg')  # ← yaha 'name' ke jagah 'msg' hona chahiye

    subject = f"New Contact Us Message from {name}"
    html_message = f"""
        <h3>New Project Inquiry</h3>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Message:</strong> {msg}</p>
    """

    try:
        send_html_mail(['abhishek.s.chauhan2002@gmail.com', 'sahilobhrai19@gmail.com'],subject,html_message)
        return Response({"success": True, "message": "Message sent successfully."})
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)


@extend_schema(request=SendOTPSerializer)
@api_view(['POST'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def send_otp(request):
    print(request.data)
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.send_otp()
        return Response({'message': 'OTP sent successfully',"success": True})
    else:
        return Response(serializer.errors, status=400)



@extend_schema(request=VerifyOTPSerializer)
@api_view(['POST'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            "message": serializer.validated_data,
            "success": True
        }, status=200)
    else:
        return Response(serializer.errors, status=400)





@extend_schema(
    request=UserUpdateSerializer,
    examples=[
        OpenApiExample(
            "Example payload",
            value={
                "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
                "firstName": "Tony",
                "lastName": "Stark",
                "email": "example@mail.com"
            },
            request_only=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_by_userId(request):
    try:
        user_id = request.data.get('userId')
        if not user_id:
            return Response({'message': 'userId is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Users.objects.get(userId=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': 'Something went wrong', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(request=AddAddressSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    serializer = AddAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Address added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def create_subscriber(request):
    serializer = SubscriberSerializer(data=request.data)
    if serializer.is_valid():
        subscriber = serializer.save()
        sendSuccessFullySubscribedMail(request.data['email'])
        return Response(SubscriberSerializer(subscriber).data, status=status.HTTP_201_CREATED)
    return Response({
        "message": serializer.errors,
        "success": False
    }, status=status.HTTP_400_BAD_REQUEST)


def sendSuccessFullySubscribedMail(email):
    html = f'''
        <!doctype html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml">
<head>
  <meta charset="utf-8">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <title>Venusa — Welcome</title>

  <!-- Web fonts (good client support). Safe fallbacks included below. -->
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Cinzel:wght@500;600&display=swap" rel="stylesheet">

  <style>
    /* Resets */
    html, body {{ margin:0 !important; padding:0 !important; height:100% !important; width:100% !important; }}
    * {{ -ms-text-size-adjust:100%; -webkit-text-size-adjust:100%; }}
    table, td {{ mso-table-lspace:0pt !important; mso-table-rspace:0pt !important; }}
    img {{ border:0; outline:none; text-decoration:none; -ms-interpolation-mode:bicubic; display:block; max-width:100%; height:auto; }}
    a {{ text-decoration:none; }}

    /* Color scheme support for dark mode */
    :root {{
      color-scheme: light dark;
      supported-color-schemes: light dark;
    }}

    /* Light mode (default) */
    .email-body {{
      background-color: #000000 !important;
      color: #ffffff !important;
    }}

    .email-container {{
      background-color: #000000 !important;
    }}

    .text-primary {{
      color: #ffffff !important;
    }}

    .text-muted {{
      color: #eaeaea !important;
    }}

    .text-subtle {{
      color: #bdbdbd !important;
    }}

    .border-rule {{
      border-color: #2a2a2a !important;
    }}

    .btn-primary {{
      background-color: #ffffff !important;
      color: #000000 !important;
      border-color: #ffffff !important;
    }}

    .btn-outline {{
      background-color: transparent !important;
      color: #ffffff !important;
      border-color: #ffffff !important;
    }}

    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {{
      .email-body {{
        background-color: #000000 !important;
        color: #ffffff !important;
      }}

      .email-container {{
        background-color: #000000 !important;
      }}

      .text-primary {{
        color: #ffffff !important;
      }}

      .text-muted {{
        color: #eaeaea !important;
      }}

      .text-subtle {{
        color: #bdbdbd !important;
      }}

      .border-rule {{
        border-color: #2a2a2a !important;
      }}

      .btn-primary {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
      }}

      .btn-outline {{
        background-color: transparent !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
      }}
    }}

    /* Light mode overrides (when user prefers light mode) */
    @media (prefers-color-scheme: light) {{
      .email-body {{
        background-color: #ffffff !important;
        color: #000000 !important;
      }}

      .email-container {{
        background-color: #ffffff !important;
      }}

      .text-primary {{
        color: #000000 !important;
      }}

      .text-muted {{
        color: #4a4a4a !important;
      }}

      .text-subtle {{
        color: #666666 !important;
      }}

      .border-rule {{
        border-color: #e0e0e0 !important;
      }}

      .btn-primary {{
        background-color: #000000 !important;
        color: #ffffff !important;
        border-color: #000000 !important;
      }}

      .btn-outline {{
        background-color: transparent !important;
        color: #000000 !important;
        border-color: #000000 !important;
      }}
    }}

    /* Typography */
    .h1 {{ 
      font-family:"Cinzel", Georgia, "Times New Roman", serif; 
      font-size:34px; 
      line-height:1.25; 
      font-weight:600; 
      letter-spacing:1px; 
    }}
    .h2 {{ 
      font-family:"Cinzel", Georgia, serif; 
      font-size:16px; 
      line-height:1.4; 
      font-weight:500; 
      letter-spacing:1.2px; 
    }}
    .body {{ 
      font-family:"IBM Plex Sans", Arial, Helvetica, sans-serif; 
      font-size:15px; 
      line-height:1.8; 
    }}
    .small {{ 
      font-size:12px; 
      line-height:1.6; 
    }}

    /* Layout helpers */
    .container {{ width:640px; max-width:100%; }}
    .px {{ padding-left:28px; padding-right:28px; }}
    .rule {{ border-top:1px solid; }}
    .card {{ border:1px solid; }}

    /* Buttons */
    .btn {{ 
      display:inline-block; 
      padding:14px 24px; 
      font-weight:600; 
      border:1px solid; 
      font-family:"IBM Plex Sans", Arial, sans-serif; 
      text-decoration: none;
    }}

    /* Responsive */
    @media (max-width:640px){{
      .px{{ padding-left:22px !important; padding-right:22px !important; }}
      .h1{{ font-size:26px !important; }}
      .stack{{ display:block !important; width:100% !important; }}
      .sp16{{ height:16px !important; line-height:16px !important; font-size:16px !important; }}
    }}

    /* Force dark mode styles for Outlook dark mode */
    [data-ogsc] .email-body {{
      background-color: #000000 !important;
      color: #ffffff !important;
    }}

    [data-ogsc] .text-primary {{
      color: #ffffff !important;
    }}

    [data-ogsc] .text-muted {{
      color: #eaeaea !important;
    }}

    [data-ogsc] .border-rule {{
      border-color: #2a2a2a !important;
    }}
  </style>

  <!--[if mso]>
    <style>
      .h1, .h2 {{ font-family: Georgia, serif !important; }}
      .body, .btn {{ font-family: Arial, sans-serif !important; }}
      .email-body {{ background-color: #000000 !important; }}
      .text-primary {{ color: #ffffff !important; }}
      .text-muted {{ color: #eaeaea !important; }}
      .border-rule {{ border-color: #2a2a2a !important; }}
    </style>
  <![endif]-->
</head>

<body class="email-body" style="background:#000; margin:0; padding:0;">
  <!-- Preheader (hidden) -->
  <div style="display:none; max-height:0; overflow:hidden; mso-hide:all;">
    Monochrome done right — welcome to Venusa. Early access, private previews, and member‑only rewards await.
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="email-container">
    <tr>
      <td align="center">
        <table role="presentation" class="container" width="640" cellpadding="0" cellspacing="0">
          <!-- Nameplate -->
          <tr>
            <td class="px" style="padding:22px 28px;" align="center">
              <div class="h2 text-primary" style="letter-spacing:6px;">VENUSA</div>
            </td>
          </tr>
          <tr><td class="px" style="padding:0 28px 18px;"><div class="rule border-rule"></div></td></tr>

          <!-- Hero -->
          <tr>
            <td class="px" style="padding:0 28px;">
              <div class="h1 text-primary" style="margin:0 0 10px;">Welcome to the Venusa Community</div>
              <div class="body text-muted" style="margin:0 0 18px;">
                Hi <strong class="text-primary">{email}</strong>, your membership opens the door to <strong class="text-primary">early drops</strong>, <strong class="text-primary">private previews</strong>, and designs built with intent.
              </div>
              <div style="padding-bottom:10px;">
                <a class="btn btn-primary" href="https://venusa.co.in">Explore the Collection →</a>
              </div>
            </td>
          </tr>

          <!-- Feature Cards -->
          <tr>
            <td class="px" style="padding:20px 28px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td class="card border-rule stack" width="50%" valign="top" style="padding:18px;">
                    <div class="h2 text-primary" style="margin:0 0 6px;">PRIORITY ACCESS</div>
                    <div class="body text-muted">Be first in line for limited releases and private previews.</div>
                  </td>
                  <td class="sp16" style="width:16px;">&nbsp;</td>
                  <td class="card border-rule stack" width="50%" valign="top" style="padding:18px;">
                    <div class="h2 text-primary" style="margin:0 0 6px;">EXCLUSIVE OFFERS</div>
                    <div class="body text-muted">Member‑only rewards tailored to how you like to shop.</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Brand Story Block -->
          <tr><td class="px" style="padding:22px 28px 0;"><div class="rule border-rule"></div></td></tr>
          <tr>
            <td class="px" style="padding:20px 28px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="card border-rule">
                <tr>
                  <td style="padding:22px;">
                    <div class="h2 text-primary" style="margin:0 0 8px;">How We Design</div>
                    <div class="body text-muted">
                      Precision lines. Enduring fabrics. A monochrome foundation that lets texture and structure lead.
                      Each silhouette is engineered to move with your day—quiet confidence, no excess.
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Product Grid (Placeholders) -->
          <tr>
            <td class="px" style="padding:20px 28px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <!-- Product 1 -->
                  <td class="stack border-rule" width="50%" valign="top" style="border:1px solid;">
                    <img src="https://venusa-bucket.blr1.cdn.digitaloceanspaces.com/venusa-bucket/products/images/1000070207.jpg" width="100%" alt="Featured product 1">
                    <table role="presentation" width="100%"><tr><td style="padding:14px 16px;">
                      <div class="h2 text-primary" style="margin:0 0 4px;">Essential Oversized Tee</div>
                      <div class="body text-muted">Soft handle. Clean drape. Built to layer.</div>
                      <div style="height:12px;"></div>
                      <a class="btn btn-outline" href="https://venusa.co.in">View Product</a>
                    </td></tr></table>
                  </td>
                  <td class="sp16" style="width:16px;">&nbsp;</td>
                  <!-- Product 2 -->
                  <td class="stack border-rule" width="50%" valign="top" style="border:1px solid;">
                    <img src="https://venusa-bucket.blr1.cdn.digitaloceanspaces.com/venusa-bucket/products/images/1000070205.jpg" width="100%" alt="Featured product 2">
                    <table role="presentation" width="100%"><tr><td style="padding:14px 16px;">
                      <div class="h2 text-primary" style="margin:0 0 4px;">Structured Midi Skirt</div>
                      <div class="body text-muted">Architectural lines. Effortless movement.</div>
                      <div style="height:12px;"></div>
                      <a class="btn btn-outline" href="https://venusa.co.in">View Product</a>
                    </td></tr></table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Quote / Testimonial -->
          <tr>
            <td class="px" style="padding:22px 28px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="card border-rule">
                <tr>
                  <td style="padding:22px;">
                    <div class="h2 text-primary" style="margin:0 0 6px;">"Less noise. More intention."</div>
                    <div class="body text-muted">Designs that feel considered—from stitch to silhouette.</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- FAQ (simple text, email-safe) -->
          <tr><td class="px" style="padding:22px 28px 0;"><div class="rule border-rule"></div></td></tr>
          <tr>
            <td class="px" style="padding:18px 28px 0;">
              <div class="h2 text-primary" style="margin:0 0 10px;">FAQs</div>
              <div class="body text-muted">
                <strong class="text-primary">When do new drops go live?</strong><br>
                Members get notified first—keep an eye on your inbox for early access links.<br><br>

                <strong class="text-primary">What sizes do you carry?</strong><br>
                Most pieces run XS–XL. Detailed size charts are on every product page.<br><br>

                <strong class="text-primary">What's your return policy?</strong><br>
                Easy 7–14 day returns on unworn items with tags; see our policy for region specifics.
              </div>
            </td>
          </tr>

          <!-- Secondary CTA -->
          <tr>
            <td align="center" style="padding:24px 28px 28px;">
              <a class="btn btn-outline" href="https://venusa.co.in">See What's New</a>
            </td>
          </tr>

          <!-- Social Strip -->
          <tr><td class="px" style="padding:0 28px 18px;"><div class="rule border-rule"></div></td></tr>
          <tr>
            <td align="center" class="body text-subtle" style="padding:12px 28px 6px;">
              Follow along
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:0 28px 22px;">
              <!-- Text links (swap for hosted icons if you prefer) -->
              <a href="https://instagram.com/venusa" class="body text-primary" style="margin:0 10px;">Instagram</a>
              <a href="https://x.com/venusa" class="body text-primary" style="margin:0 10px;">X</a>
              <a href="https://pinterest.com/venusa" class="body text-primary" style="margin:0 10px;">Pinterest</a>
              <a href="https://www.facebook.com/venusa/" class="body text-primary" style="margin:0 10px;">Facebook</a>
            </td>
          </tr>

          <!-- Footer -->
          <tr><td class="px" style="padding:0 28px 12px;"><div class="rule border-rule"></div></td></tr>
          <tr>
            <td class="body small text-subtle" align="center" style="padding:8px 28px 22px;">
              You're receiving this because you joined the Venusa community.<br>
              <a href="https://webservices.venusa.co.in/unsubscribe?email={email}" class="text-primary">Manage preferences</a> •
              <a href="https://webservices.venusa.co.in/unsubscribe?email={email}" class="text-primary">Unsubscribe</a><br>
              Venusa, C-608B, JVTS GARDEN, CHATTARPUR, NEW DELHI South West Delhi DELHI,
              110074
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
    '''
    subject = "Welcome to VENUSA"
    send_html_mail(email, subject, html)
















