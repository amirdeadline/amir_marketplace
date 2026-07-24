import * as fs from 'fs';
import * as path from 'path';
import Ajv, { type ErrorObject, type ValidateFunction } from 'ajv';
import { schemasDir } from './pluginRoot';

export interface ValidationResult {
  ok: boolean;
  errors: string[];
}

export class SchemaValidator {
  private readonly ajv = new Ajv({ allErrors: true, strict: false });
  private readonly cache = new Map<string, ValidateFunction>();
  private pluginRoot: string | undefined;

  setPluginRoot(pluginRoot: string | undefined): void {
    this.pluginRoot = pluginRoot;
    this.cache.clear();
  }

  validate(schemaFile: string, data: unknown): ValidationResult {
    if (!this.pluginRoot) {
      return { ok: false, errors: ['Plugin root not resolved; cannot validate schemas'] };
    }
    try {
      const validate = this.load(schemaFile);
      const ok = validate(data) as boolean;
      if (ok) return { ok: true, errors: [] };
      const errors = (validate.errors || []).map((e: ErrorObject) =>
        `${e.instancePath || '/'} ${e.message || 'invalid'}`,
      );
      return { ok: false, errors };
    } catch (err) {
      return {
        ok: false,
        errors: [err instanceof Error ? err.message : String(err)],
      };
    }
  }

  private load(schemaFile: string): ValidateFunction {
    const cached = this.cache.get(schemaFile);
    if (cached) return cached;
    const full = path.join(schemasDir(this.pluginRoot!), schemaFile);
    const schema = JSON.parse(fs.readFileSync(full, 'utf8')) as object;
    const validate = this.ajv.compile(schema);
    this.cache.set(schemaFile, validate);
    return validate;
  }
}
