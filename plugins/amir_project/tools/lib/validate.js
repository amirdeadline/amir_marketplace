'use strict';

const fs = require('fs');
const path = require('path');

const SCHEMA_CACHE = new Map();

function loadSchema(name) {
  if (SCHEMA_CACHE.has(name)) {
    return SCHEMA_CACHE.get(name);
  }
  const schemaPath = path.join(__dirname, '..', '..', 'schemas', name);
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  SCHEMA_CACHE.set(name, schema);
  return schema;
}

function joinPath(base, segment) {
  if (!segment) return base;
  if (segment.startsWith('/')) {
    return base + segment;
  }
  return base ? `${base}.${segment}` : segment;
}

function typeOf(value) {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  return typeof value;
}

function matchesType(value, expected) {
  if (Array.isArray(expected)) {
    return expected.some((t) => matchesType(value, t));
  }
  if (expected === 'integer') {
    return typeof value === 'number' && Number.isInteger(value);
  }
  if (expected === 'number') {
    return typeof value === 'number' && !Number.isNaN(value);
  }
  return typeOf(value) === expected;
}

function validate(schema, data, basePath = '') {
  const errors = [];

  function fail(message) {
    errors.push(basePath ? `${basePath}: ${message}` : message);
  }

  function pushErrors(subErrors, prefix) {
    for (const err of subErrors) {
      errors.push(joinPath(prefix, err));
    }
  }

  function validateValue(value, subSchema, currentPath) {
    const localErrors = [];

    function localFail(message) {
      localErrors.push(currentPath ? `${currentPath}: ${message}` : message);
    }

    if (subSchema.oneOf) {
      const branchErrors = [];
      let validBranches = 0;
      for (const branch of subSchema.oneOf) {
        const result = validate(branch, value, currentPath);
        if (result.ok) {
          validBranches += 1;
        } else {
          branchErrors.push(result.errors);
        }
      }
      if (validBranches !== 1) {
        localFail(`must match exactly one schema in oneOf (matched ${validBranches})`);
      }
      return localErrors;
    }

    if (subSchema.anyOf) {
      let anyValid = false;
      for (const branch of subSchema.anyOf) {
        const result = validate(branch, value, currentPath);
        if (result.ok) {
          anyValid = true;
          break;
        }
      }
      if (!anyValid) {
        localFail('must match at least one schema in anyOf');
      }
      return localErrors;
    }

    if (subSchema.enum) {
      if (!subSchema.enum.includes(value)) {
        localFail(`must be one of ${JSON.stringify(subSchema.enum)}`);
      }
      return localErrors;
    }

    if (subSchema.type !== undefined) {
      if (!matchesType(value, subSchema.type)) {
        const expected = Array.isArray(subSchema.type) ? subSchema.type.join('|') : subSchema.type;
        localFail(`must be type ${expected}, got ${typeOf(value)}`);
        return localErrors;
      }
    }

    if (subSchema.pattern !== undefined && typeof value === 'string') {
      const re = new RegExp(subSchema.pattern);
      if (!re.test(value)) {
        localFail(`must match pattern ${subSchema.pattern}`);
      }
    }

    if (subSchema.minimum !== undefined && typeof value === 'number') {
      if (value < subSchema.minimum) {
        localFail(`must be >= ${subSchema.minimum}`);
      }
    }

    if (subSchema.maximum !== undefined && typeof value === 'number') {
      if (value > subSchema.maximum) {
        localFail(`must be <= ${subSchema.maximum}`);
      }
    }

    if (subSchema.minLength !== undefined && typeof value === 'string') {
      if (value.length < subSchema.minLength) {
        localFail(`must have length >= ${subSchema.minLength}`);
      }
    }

    if (subSchema.minItems !== undefined && Array.isArray(value)) {
      if (value.length < subSchema.minItems) {
        localFail(`must have at least ${subSchema.minItems} items`);
      }
    }

    if (subSchema.required && typeof value === 'object' && value !== null && !Array.isArray(value)) {
      for (const key of subSchema.required) {
        if (!(key in value)) {
          localFail(`missing required property "${key}"`);
        }
      }
    }

    if (subSchema.properties && typeof value === 'object' && value !== null && !Array.isArray(value)) {
      for (const [key, propSchema] of Object.entries(subSchema.properties)) {
        if (key in value) {
          const childErrors = validateValue(value[key], propSchema, joinPath(currentPath, key));
          localErrors.push(...childErrors);
        }
      }
    }

    if (subSchema.additionalProperties === false && typeof value === 'object' && value !== null && !Array.isArray(value)) {
      const allowed = new Set([
        ...(subSchema.required || []),
        ...Object.keys(subSchema.properties || {}),
      ]);
      for (const key of Object.keys(value)) {
        if (!allowed.has(key)) {
          localFail(`additional property "${key}" is not allowed`);
        }
      }
    }

    if (subSchema.items && Array.isArray(value)) {
      value.forEach((item, index) => {
        const childErrors = validateValue(item, subSchema.items, joinPath(currentPath, String(index)));
        localErrors.push(...childErrors);
      });
    }

    if (subSchema.$ref) {
      const ref = subSchema.$ref;
      let resolved = null;
      if (ref.startsWith('#/$defs/')) {
        resolved = schema.$defs && schema.$defs[ref.slice('#/$defs/'.length)];
      } else if (ref.startsWith('#/definitions/')) {
        resolved = schema.definitions && schema.definitions[ref.slice('#/definitions/'.length)];
      }
      if (resolved) {
        const childErrors = validateValue(value, resolved, currentPath);
        localErrors.push(...childErrors);
      } else {
        localFail(`unknown $ref ${ref}`);
      }
    }

    return localErrors;
  }

  const rootErrors = validateValue(data, schema, basePath);
  pushErrors(rootErrors, '');

  return { ok: errors.length === 0, errors };
}

function validateFile(schemaName, data) {
  const schema = loadSchema(schemaName);
  return validate(schema, data);
}

module.exports = {
  validate,
  validateFile,
  loadSchema,
};
