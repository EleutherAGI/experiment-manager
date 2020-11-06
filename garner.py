class UserObj:
    def __init__(
        self, username, attribute_list, cognito_obj, metadata=None, attr_map=None
    ):
        """
        :param username:
        :param attribute_list:
        :param metadata: Dictionary of User metadata
        """
        self.username = username
        self._cognito = cognito_obj
        self._attr_map = {} if attr_map is None else attr_map
        self._data = cognito_to_dict(attribute_list, self._attr_map)
        self.sub = self._data.pop("sub", None)
        self.email_verified = self._data.pop("email_verified", None)
        self.phone_number_verified = self._data.pop("phone_number_verified", None)
        self._metadata = {} if metadata is None else metadata

    def __repr__(self):
        return "<{class_name}: {uni}>".format(
            class_name=self.__class__.__name__, uni=self.__unicode__()
        )

    def __unicode__(self):
        return self.username

    def __getattr__(self, name):
        if name in list(self.__dict__.get("_data", {}).keys()):
            return self._data.get(name)
        if name in list(self.__dict__.get("_metadata", {}).keys()):
            return self._metadata.get(name)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in list(self.__dict__.get("_data", {}).keys()):
            self._data[name] = value
        else:
            super(UserObj, self).__setattr__(name, value)

    def save(self, admin=False):
        if admin:
            self._cognito.admin_update_profile(self._data, self._attr_map)
            return
        self._cognito.update_profile(self._data, self._attr_map)

    def delete(self, admin=False):
        if admin:
            self._cognito.admin_delete_user()
            return
        self._cognito.delete_user()
        
class GroupObj:
    def __init__(self, group_data, cognito_obj):
        """
        :param group_data: a dictionary with information about a group
        :param cognito_obj: an instance of the Cognito class
        """
        self._data = group_data
        self._cognito = cognito_obj
        self.group_name = self._data.pop("GroupName", None)
        self.description = self._data.pop("Description", None)
        self.creation_date = self._data.pop("CreationDate", None)
        self.last_modified_date = self._data.pop("LastModifiedDate", None)
        self.role_arn = self._data.pop("RoleArn", None)
        self.precedence = self._data.pop("Precedence", None)

    def __unicode__(self):
        return self.group_name

    def __repr__(self):
        return "<{class_name}: {uni}>".format(
            class_name=self.__class__.__name__, uni=self.__unicode__()
        )
    
class Garner:
    
    user_class = UserObj
    group_class = GroupObj
    
    def __init__(self, username=None, secret_key=None, password=None):
        
        self.user_pool_id = config["aws_user_pools_id"]
        self.user_pool_region = config["aws_cognito_region"]
        self.client_id = config["aws_user_pools_web_client_id"]
        
        self.username = username
        
        self.refresh_token = None
        self.client_secret = None
        self.token_type = None
        self.custom_attributes = None
        self.base_attributes = None
        self.pool_jwk = None
        
        self.client = boto3.client("cognito-idp")
        
        self.authenticate(password)
        
    def authenticate(self, password):
        """
        Authenticate the user using the SRP protocol
        :param password: The user's passsword
        :return:
        """
        if not password:
            print("Enter Password")
        aws = AWSSRP(
            username=self.username,
            password=(password if password else getpass("Password:")),
            pool_id=self.user_pool_id,
            client_id=self.client_id,
            client=self.client,
            client_secret=self.client_secret,
        )
        tokens = aws.authenticate_user('Password:')
        print("Authenticated")
        self.verify_token(tokens["AuthenticationResult"]["IdToken"], "id_token", "id")
        self.refresh_token = tokens["AuthenticationResult"]["RefreshToken"]
        self.verify_token(
            tokens["AuthenticationResult"]["AccessToken"], "access_token", "access"
        )
        self.token_type = tokens["AuthenticationResult"]["TokenType"]
        
    def get_keys(self):
        if self.pool_jwk:
            return self.pool_jwk

        # Check for the dictionary in environment variables.
        pool_jwk_env = env("COGNITO_JWKS", {}, var_type="dict")
        if pool_jwk_env:
            self.pool_jwk = pool_jwk_env
        # If it is not there use the requests library to get it
        else:
            self.pool_jwk = requests.get(
                "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
                    self.user_pool_region, self.user_pool_id
                )
            ).json()
        return self.pool_jwk

    def get_key(self, kid):
        keys = self.get_keys().get("keys")
        key = list(filter(lambda x: x.get("kid") == kid, keys))
        return key[0]
    
    def verify_token(self, token, id_name, token_use):
        kid = jwt.get_unverified_header(token).get("kid")
        unverified_claims = jwt.get_unverified_claims(token)
        token_use_verified = unverified_claims.get("token_use") == token_use
        if not token_use_verified:
            raise TokenVerificationException("Your {} token use could not be verified.")
        hmac_key = self.get_key(kid)
        try:
            verified = jwt.decode(
                token,
                hmac_key,
                algorithms=["RS256"],
                audience=unverified_claims.get("aud"),
                issuer=unverified_claims.get("iss"),
            )
        except JWTError:
            raise TokenVerificationException("Your {} token could not be verified.")
        setattr(self, id_name, token)
        return verified