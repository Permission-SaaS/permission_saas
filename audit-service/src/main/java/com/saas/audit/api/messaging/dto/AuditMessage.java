package com.saas.audit.api.messaging.dto;

import java.time.Instant;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import tools.jackson.databind.JsonNode;

/**
 * Envelope de toda mensagem da fila de auditoria. O {@code payload} chega como JSON
 * cru e só é convertido depois que o {@code type} diz o que ele é: assim o mesmo
 * envelope serve a qualquer tipo de evento e a qualquer sistema que publique.
 */
public record AuditMessage(
        @NotBlank String source,
        @NotBlank String type,
        @NotNull Instant occurredAt,
        @NotNull JsonNode payload) {
}
