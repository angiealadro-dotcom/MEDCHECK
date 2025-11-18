import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import type { User } from '../db/schema';

const SALT_ROUNDS = 10;

// Password utilities
export async function hashPassword(password: string): Promise<string> {
  return await bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  return await bcrypt.compare(password, hashedPassword);
}

// JWT utilities
export interface TokenPayload {
  sub: string; // user id
  username: string;
  organizationId: number;
  isAdmin: boolean;
  isSuperAdmin: boolean;
  exp: number;
}

export function createAccessToken(user: User, secretKey: string, expiresInMinutes: number = 30): string {
  const exp = Math.floor(Date.now() / 1000) + (expiresInMinutes * 60);

  const payload: TokenPayload = {
    sub: user.id.toString(),
    username: user.username,
    organizationId: user.organizationId,
    isAdmin: user.isAdmin,
    isSuperAdmin: user.isSuperAdmin,
    exp,
  };

  return jwt.sign(payload, secretKey, { algorithm: 'HS256' });
}

export function verifyToken(token: string, secretKey: string): TokenPayload | null {
  try {
    const decoded = jwt.verify(token, secretKey, { algorithms: ['HS256'] });
    return decoded as TokenPayload;
  } catch (error) {
    console.error('Token verification failed:', error);
    return null;
  }
}

export function extractBearerToken(authHeader: string | undefined): string | null {
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }
  return authHeader.substring(7);
}
