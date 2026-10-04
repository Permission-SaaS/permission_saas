package com.saas.audit.domain;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;

@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class PermissionCheckEvent extends AuditEvent {

    public static final String TYPE = "PERMISSION_CHECK";

    private String routePath;
    private String httpMethod;
    private String roleName;

    private boolean granted;

    private String reason;

    private double durationMs;

    private String ipAddress;
    private String country;

    @Override
    public String describe() {
        return (granted ? "PERMITIDO" : "NEGADO")
                + " " + httpMethod + " " + routePath
                + " para o cargo '" + roleName + "'"
                + (granted ? "" : " — " + reason)
                + " (" + durationMs + " ms)";
    }

    @Override
    public String type() {
        return TYPE;
    }
}
