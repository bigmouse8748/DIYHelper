/**
 * AWS Amplify Configuration for Cognito
 */

export const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'us-east-1_KNXXo2xyx',
      userPoolClientId: 'm8773nbntsdncpflvld1dfum9',
      signUpVerificationMethod: 'code',
      loginWith: {
        email: true,
        username: false
      },
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: false
      }
    }
  }
}

// User group permissions mapping
export const USER_GROUPS = {
  free: {
    diy_assistant: true,
    tool_identification: true, // All registered users can use tool identification
    daily_quota: 5,
    priority_support: false,
    admin_features: false
  },
  pro: {
    diy_assistant: true,
    tool_identification: true,
    daily_quota: 20,
    priority_support: false,
    admin_features: false
  },
  premium: {
    diy_assistant: true,
    tool_identification: true,
    daily_quota: 50,
    priority_support: true,
    admin_features: false
  },
  admin: {
    diy_assistant: true,
    tool_identification: true,
    daily_quota: -1, // Unlimited
    priority_support: true,
    admin_features: true
  }
}