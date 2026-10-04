package com.saas.audit.api.messaging;

import java.time.ZoneOffset;
import java.util.Set;

import org.springframework.amqp.AmqpRejectAndDontRequeueException;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import com.saas.audit.api.messaging.dto.AuditMessage;
import com.saas.audit.api.messaging.dto.PermissionCheckPayload;
import com.saas.audit.application.RegisterPermissionCheckUseCase;
import com.saas.audit.application.command.RegisterPermissionCheckCommand;
import com.saas.audit.domain.AuditEvent;
import com.saas.audit.domain.PermissionCheckEvent;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.json.JsonMapper;

/**
 * Consumidor da fila de auditoria: a mesma gravação do POST /audit-events/permission-checks,
 * com a mensagem no lugar da requisição HTTP. Uma mensagem que nunca vai ser gravável
 * (tipo desconhecido, payload inválido) é rejeitada sem voltar para a fila e cai na
 * fila de mensagens mortas.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AuditMessageListener {

    private final RegisterPermissionCheckUseCase registerPermissionCheckUseCase;

    private final JsonMapper jsonMapper;

    private final Validator validator;

    @RabbitListener(queues = "${audit.messaging.queue}")
    public void on(AuditMessage message) {
        reject(validator.validate(message));

        if (!PermissionCheckEvent.TYPE.equals(message.type())) {
            throw new AmqpRejectAndDontRequeueException("Unsupported audit message type: " + message.type());
        }

        PermissionCheckPayload payload = toPermissionCheckPayload(message);
        reject(validator.validate(payload));

        AuditEvent saved = registerPermissionCheckUseCase.execute(new RegisterPermissionCheckCommand(
                payload.projectId(),
                message.occurredAt().atOffset(ZoneOffset.UTC),
                payload.routePath(),
                payload.httpMethod(),
                payload.roleName(),
                payload.granted(),
                payload.reason(),
                payload.durationMs()));

        log.info("Audit message from {} registered: {}", message.source(), saved.describe());
    }

    private PermissionCheckPayload toPermissionCheckPayload(AuditMessage message) {
        try {
            return jsonMapper.treeToValue(message.payload(), PermissionCheckPayload.class);
        } catch (JacksonException e) {
            throw new AmqpRejectAndDontRequeueException("Malformed " + message.type() + " payload", e);
        }
    }

    private static void reject(Set<? extends ConstraintViolation<?>> violations) {
        if (!violations.isEmpty()) {
            throw new AmqpRejectAndDontRequeueException("Invalid audit message: " + violations.stream()
                    .map(v -> v.getPropertyPath() + " " + v.getMessage())
                    .sorted()
                    .toList());
        }
    }

}
